import datetime
import time
import random
import os

LOG_FILE_PATH = os.path.join('data', 'system_logs.log')
LOG_INTERVAL_SECONDS = 0.001
ANOMALY_PROBABILITY = 0.05
NUM_LOGS_TO_GENERATE = 50000

LOG_LEVELS = ["INFO", "DEBUG", "WARN", "ERROR", "CRITICAL"]
EVENT_TYPES = ["LOGIN", "FILE_ACCESS", "NETWORK_CONN", "PROCESS_START", "AUTH_ATTEMPT"]
USERNAMES = ["UserA", "UserB", "AdminX", "GuestY", "ServiceZ"]
RESOURCES = ["/var/log/syslog", "/etc/passwd", "/data/reports/sales.csv", "192.168.1.1:80", "public_s3_bucket"]
STATUSES = ["SUCCESS", "FAILURE", "DENIED", "TIMEOUT"]

NORMAL_IPS = [f"192.168.1.{i}" for i in range(10, 50)] + [f"10.0.0.{i}" for i in range(100, 120)]
MALICIOUS_IPS = ["203.0.113.1", "172.16.0.250", "91.198.174.192"]

ANOMALIES = [
    {
        "level": "ERROR",
        "event_type": "LOGIN_FAILED",
        "source_ip": lambda: random.choice(MALICIOUS_IPS),
        "target_resource": lambda: random.choice(USERNAMES),
        "status": "FAILURE",
        "message": "Multiple failed login attempts from unusual IP.",
        "weight": 3
    },
    {
        "level": "CRITICAL",
        "event_type": "FILE_ACCESS",
        "source_ip": lambda: random.choice(NORMAL_IPS[:5]),
        "target_resource": "/etc/passwd",
        "status": "DENIED",
        "message": "Unauthorized access attempt to sensitive system file.",
        "weight": 2
    },
    {
        "level": "WARN",
        "event_type": "NETWORK_CONN",
        "source_ip": lambda: random.choice(NORMAL_IPS),
        "target_resource": "external.malicious.com:443",
        "status": "TIMEOUT",
        "message": "Outbound connection to known suspicious domain timed out.",
        "weight": 1
    }
]

ANOMALY_WEIGHTS = [a["weight"] for a in ANOMALIES]
ANOMALY_CHOICES = ANOMALIES

def generate_normal_log():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = random.choice(["INFO", "DEBUG"])
    event_type = random.choice(EVENT_TYPES)
    source_ip = random.choice(NORMAL_IPS)
    username = random.choice(USERNAMES)
    target_resource = random.choice(RESOURCES)
    status = random.choice(["SUCCESS"])
    message = f"{username} {event_type.replace('_', ' ').lower()} {target_resource} from {source_ip} - {status}."
    return f"{timestamp},{level},{event_type},{source_ip},{target_resource},{status},{message}"

def generate_anomaly_log():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    anomaly_def = random.choices(ANOMALY_CHOICES, weights=ANOMALY_WEIGHTS, k=1)[0]
    level = anomaly_def["level"]
    event_type = anomaly_def["event_type"]
    source_ip = anomaly_def["source_ip"]() if callable(anomaly_def["source_ip"]) else anomaly_def["source_ip"]
    target_resource = anomaly_def["target_resource"]() if callable(anomaly_def["target_resource"]) else anomaly_def["target_resource"]
    status = anomaly_def["status"]
    message = anomaly_def["message"]
    return f"{timestamp},{level},{event_type},{source_ip},{target_resource},{status},{message}"

def ensure_log_directory():
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

def run_log_generator():
    ensure_log_directory()
    log_count = 0
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting log generation. Writing to '{LOG_FILE_PATH}'...")
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Press Ctrl+C to stop.")

    with open(LOG_FILE_PATH, 'w') as f:
        f.write("")

    while True:
        if NUM_LOGS_TO_GENERATE is not None and log_count >= NUM_LOGS_TO_GENERATE:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Reached {NUM_LOGS_TO_GENERATE} logs. Stopping generator.")
            break

        if random.random() < ANOMALY_PROBABILITY:
            log_line = generate_anomaly_log()
            print(f"  [ANOMALY GENERATED] {log_line}")
        else:
            log_line = generate_normal_log()

        with open(LOG_FILE_PATH, 'a') as f:
            f.write(log_line + "\n")

        log_count += 1
        time.sleep(LOG_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        run_log_generator()
    except KeyboardInterrupt:
        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Log generation stopped by user.")
