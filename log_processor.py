import datetime
import random
import time
import os
import zlib
import re
import json 

import pandas as pd
from sklearn.ensemble import IsolationForest
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID, NUMERIC, STORED 
from whoosh.writing import AsyncWriter
import csv
from io import StringIO

LOG_FILE_PATH = os.path.join('data', 'system_logs.log')
WHOOSH_INDEX_DIR = 'whoosh_index' 
PROCESS_INTERVAL_SECONDS = 0.5
TRAINING_LOG_COUNT = 35000 
ISOLATION_FOREST_CONTAMINATION = 0.01 
FEATURE_BUFFER_SIZE = 100

log_schema = Schema(
    log_id=ID(stored=True, unique=True),
    timestamp=DATETIME(stored=True, sortable=True),
    level=KEYWORD(stored=True),
    event_type=KEYWORD(stored=True),
    source_ip=ID(stored=True),
    target_resource=KEYWORD(stored=True),
    status=KEYWORD(stored=True),
    message_raw=TEXT(stored=True),
    full_log_compressed=STORED(),
)

idx = None
writer = None
isolation_forest_model = None
log_file_position = 0
feature_buffer_with_logs = []

LEVEL_MAP = {
    "DEBUG": 0, "INFO": 1, "WARN": 2, "WARNING": 2, "ERROR": 3, "CRITICAL": 4, "FATAL": 4
}
EVENT_TYPE_MAP = {
    "LOGIN": 0, "FILE_ACCESS": 1, "NETWORK_CONN": 2, "PROCESS_START": 3,
    "AUTH_ATTEMPT": 4, "LOGIN_FAILED": 5, "DATA_EXFIL": 6, "PROCESS_END": 7,
    "DB_CONNECTION_FAILED": 8, "SERVICE_RESTART": 9, "FILE_ACCESS_DENIED": 10,
    "NETWORK_ISSUE": 11
}

def ensure_whoosh_index():
    global idx, writer

    if not os.path.exists(WHOOSH_INDEX_DIR):
        os.makedirs(WHOOSH_INDEX_DIR)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Created index directory: '{WHOOSH_INDEX_DIR}'")

    if exists_in(WHOOSH_INDEX_DIR):
        try:
            idx = open_dir(WHOOSH_INDEX_DIR)
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Opened existing Whoosh index at '{WHOOSH_INDEX_DIR}'")
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error opening existing index: {e}. Attempting to recreate index.")
            import shutil
            shutil.rmtree(WHOOSH_INDEX_DIR)
            os.makedirs(WHOOSH_INDEX_DIR)
            idx = create_in(WHOOSH_INDEX_DIR, log_schema)
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Recreated Whoosh index due to error.")
    else:
        idx = create_in(WHOOSH_INDEX_DIR, log_schema)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Created new Whoosh index at '{WHOOSH_INDEX_DIR}'")

    writer = AsyncWriter(idx)

def extract_features(log_line_parts):
    level_num = LEVEL_MAP.get(log_line_parts[1], -1)
    event_type_num = EVENT_TYPE_MAP.get(log_line_parts[2], -1)
    is_failure = 1 if log_line_parts[5].upper() == "FAILURE" else 0
    is_suspicious_keyword = 1 if re.search(r'unusual|unauthorized|failed attempt|denied|failed to connect', log_line_parts[6], re.IGNORECASE) else 0

    try:
        log_dt = datetime.datetime.strptime(log_line_parts[0], "%Y-%m-%d %H:%M:%S")
        minute_of_day = log_dt.hour * 60 + log_dt.minute
        day_of_week = log_dt.weekday()
    except ValueError:
        minute_of_day = 0
        day_of_week = -1

    return [
        level_num,
        event_type_num,
        is_failure,
        is_suspicious_keyword,
        minute_of_day,
        day_of_week
    ]

def train_anomaly_detector(initial_logs_features):
    global isolation_forest_model
    if not initial_logs_features:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] No initial logs provided for training. Skipping model training.")
        return

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Training Isolation Forest model with {len(initial_logs_features)} initial logs...")

    X_train = pd.DataFrame(initial_logs_features)

    isolation_forest_model = IsolationForest(
        random_state=42,
        contamination=ISOLATION_FOREST_CONTAMINATION,
        n_estimators=100,
        max_features=1.0
    )
    isolation_forest_model.fit(X_train)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Isolation Forest model trained.")

def process_log_entry(raw_log_line):
    global feature_buffer_with_logs

    log_io = StringIO(raw_log_line)
    reader = csv.reader(log_io)

    try:
        parts = next(reader)
        if len(parts) != 7:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] WARNING: Malformed log line (parts mismatch), skipping: {raw_log_line.strip()}")
            return
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] WARNING: Failed to parse log line with CSV reader, skipping: {raw_log_line.strip()} - {e}")
        return

    try:
        log_datetime = datetime.datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] WARNING: Invalid timestamp format in log, skipping: {parts[0]}")
        return

    current_features = extract_features(parts)
    feature_buffer_with_logs.append({"features": current_features, "raw_log": raw_log_line})

    if isolation_forest_model and len(feature_buffer_with_logs) >= FEATURE_BUFFER_SIZE:
        features_for_prediction = [item["features"] for item in feature_buffer_with_logs]
        predictions = isolation_forest_model.predict(features_for_prediction)

        for i, prediction in enumerate(predictions):
            if prediction == -1:
                anomalous_log_data = feature_buffer_with_logs[i]
                print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] !!! ANOMALY DETECTED !!!")
                print(f"  Log (parsed from buffer): {anomalous_log_data['raw_log'].strip()}")

        feature_buffer_with_logs.clear()

    log_id = f"{log_datetime.strftime('%Y%m%d%H%M%S%f')}_{random.randint(0,99999)}"
    compressed_log_bytes = zlib.compress(raw_log_line.encode('utf-8'))

    writer.add_document(
        log_id=log_id,
        timestamp=log_datetime,
        level=parts[1],
        event_type=parts[2],
        source_ip=parts[3],
        target_resource=parts[4],
        status=parts[5],
        message_raw=parts[6],
        full_log_compressed=compressed_log_bytes
    )

def run_log_processor():
    global log_file_position

    ensure_whoosh_index()

    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting log processor...")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Waiting for initial logs for training ({TRAINING_LOG_COUNT} lines)...")

    initial_training_data_features = []
    initial_log_lines_read = 0
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            while initial_log_lines_read < TRAINING_LOG_COUNT:
                line = f.readline()
                if not line:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] WARNING: End of log file reached. Not enough initial logs for training ({initial_log_lines_read}/{TRAINING_LOG_COUNT}). Model robustness might be affected.")
                    break

                log_io = StringIO(line.strip())
                reader = csv.reader(log_io)
                try:
                    parts = next(reader)
                    if len(parts) == 7:
                        features = extract_features(parts)
                        initial_training_data_features.append(features)
                        initial_log_lines_read += 1
                except Exception as e:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Skipping malformed line during training data collection: {line.strip()} ({e})")

            log_file_position = f.tell()

    except FileNotFoundError:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ERROR: Log file '{LOG_FILE_PATH}' not found for initial training. Please ensure log_generator.py is running and creating logs.")
        return

    train_anomaly_detector(initial_training_data_features)

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Entering real-time log monitoring mode...")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Monitoring '{LOG_FILE_PATH}' for new logs...")

    while True:
        try:
            with open(LOG_FILE_PATH, 'r') as f:
                f.seek(log_file_position)
                new_logs = f.readlines()
                log_file_position = f.tell()

            if new_logs:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Processed {len(new_logs)} new log entries.")
                for line in new_logs:
                    process_log_entry(line.strip())
                writer.commit()

            time.sleep(PROCESS_INTERVAL_SECONDS)

        except FileNotFoundError:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Log file '{LOG_FILE_PATH}' not found. Waiting for it to appear...")
            time.sleep(PROCESS_INTERVAL_SECONDS * 5)
        except KeyboardInterrupt:
            print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Log processor stopped by user. Finalizing index writes...")
            writer.close()
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Index writer closed.")
            break
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] An unexpected error occurred in main loop: {e}")
            time.sleep(PROCESS_INTERVAL_SECONDS * 2)

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
        print(f"Created data directory: {os.path.abspath('data')}")

    run_log_processor()
