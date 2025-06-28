````markdown
# Real-time Log Monitoring & Anomaly Detection

## Project Description
LogGuard is a Python-based prototype system designed for comprehensive log management, analysis, and security monitoring. It demonstrates an end-to-end workflow including synthetic log generation, real-time log processing, machine learning-driven anomaly detection, efficient data compression, and a robust search interface for investigative analysis.

**Key Features:**
* **Synthetic Log Generation:** Creates realistic system logs with configurable anomaly injection.
* **Stream Processing:** Reads and processes log data in a continuous, streaming fashion.
* **Anomaly Detection:** Utilizes an Isolation Forest model to identify unusual patterns and potential threats.
* **Data Compression:** Compresses raw log lines using Zlib for efficient storage.
* **Searchable Indexing:** Builds a high-performance search index using Whoosh, allowing rapid querying of log data.
* **Interactive Search Interface:** Provides a command-line tool for powerful keyword and field-specific searches.

## Table of Contents
1.  [Prerequisites](#prerequisites)
2.  [Getting Started](#getting-started)
    * [Step 1: Clone the Repository](#step-1-clone-the-repository)
    * [Step 2: Navigate into the Project Directory](#step-2-navigate-into-the-project-directory)
    * [Step 3: Create a Python Virtual Environment](#step-3-create-a-python-virtual-environment)
    * [Step 4: Activate the Virtual Environment](#step-4-activate-the-virtual-environment)
    * [Step 5: Install Project Dependencies](#step-5-install-project-dependencies)
3.  [Running LogGuard](#running-logguard)
    * [Phase 1: Generate Initial Log Data](#phase-1-generate-initial-log-data)
    * [Phase 2: Process Logs and Detect Anomalies](#phase-2-process-logs-and-detect-anomalies)
    * [Phase 3: Search and Investigate Logs](#phase-3-search-and-investigate-logs)
    * [Optional: Simulating Live Log Streams](#optional-simulating-live-log-streams)
4.  [Cleaning Up (Optional)](#cleaning-up-optional)
5.  [Project Structure](#project-structure)
6.  [License](#license)
7.  [Contact](#contact)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Git:** For cloning the repository.
* **Python 3.8+:** The project is developed using Python.
* **pip:** Python's package installer (usually comes with Python).

## Getting Started

Follow these steps to set up and run the LogGuard project:

### Step 1: Clone the Repository

Open your Git Bash (or terminal for Linux/macOS, Command Prompt for Windows) and clone the project to your local machine:

```bash
git clone [https://github.com/akashhbais/log-monitor.git](https://github.com/akashhbais/log-monitor.git)
````

### Step 2: Navigate into the Project Directory

Change your current directory to the project's root folder:

```bash
cd log-monitor/logguard
```

### Step 3: Create a Python Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies. This isolates the project's packages from your system-wide Python installation.

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

You need to activate the virtual environment in *each* new terminal session you open to work on the project.

  * **On Windows (Git Bash):**
    ```bash
    source venv/Scripts/activate
    ```
  * **On Linux / macOS (Bash/Zsh):**
    ```bash
    source venv/bin/activate
    ```
    You'll know it's activated when your terminal prompt changes, usually by adding `(venv)` at the beginning.

### Step 5: Install Project Dependencies

The project relies on several Python libraries. Install them using pip:

1.  **Generate `requirements.txt` (If you haven't already and plan to push it):**
    If you're setting up the project initially and want to ensure all current dependencies are captured for others, run this *from your activated venv*:

    ```bash
    pip freeze > requirements.txt
    ```

    Then, make sure to add and commit `requirements.txt` to your GitHub repository.

2.  **Install dependencies (for a new user or fresh setup):**

    ```bash
    pip install -r requirements.txt
    ```

    This will install `scikit-learn`, `pandas`, `Whoosh`, and other necessary packages.

## Running LogGuard

LogGuard operates in three main phases. You will typically run `log_generator.py`, `log_processor.py`, and `log_searcher.py` in **separate terminal windows** to simulate a continuous workflow.

### Phase 1: Generate Initial Log Data

First, generate a batch of synthetic logs to populate your system.

1.  **Open a NEW terminal window** (e.g., Git Bash).
2.  **Navigate to your `logguard` directory and activate the `venv`** (as shown in Steps 2 & 4 above).
3.  **Run the log generator:**
    ```bash
    python log_generator.py
    ```
    This will create a `data/system_logs.log` file (e.g., 50,000 logs by default). This process might take a few moments depending on the `LOG_INTERVAL_SECONDS` setting in `log_generator.py`.

### Phase 2: Process Logs and Detect Anomalies

This script continuously monitors `system_logs.log`, trains an anomaly detection model, processes all logs (detecting anomalies in the latter part), compresses the raw data, and builds a searchable Whoosh index.

1.  **Open a SECOND, NEW terminal window.**
2.  **Navigate to your `logguard` directory and activate the `venv`** (as shown in Steps 2 & 4 above).
3.  **Run the log processor:**
    ```bash
    python log_processor.py
    ```
      * Observe the terminal for messages indicating model training and anomaly detection.
      * This process will take some time as it works through all the generated logs. Let it complete until you see it settles into a "waiting for new logs" state.
      * A `whoosh_index` directory will be created inside `logguard/`.

### Phase 3: Search and Investigate Logs

Once the `log_processor.py` has finished indexing all logs, you can use the search utility to query the indexed data.

1.  **Open a THIRD, NEW terminal window.**
2.  **Navigate to your `logguard` directory and activate the `venv`** (as shown in Steps 2 & 4 above).
3.  **Run the log searcher:**
    ```bash
    python log_searcher.py
    ```
      * You'll see a `LogSearch >` prompt.
      * **Enter your search queries:**
          * **Basic Keyword:** `failed login`
          * **Specific Level:** `level:ERROR`
          * **IP Address:** `source_ip:203.0.113.1` (try your generated malicious IPs\!)
          * **Event Type:** `event_type:FILE_ACCESS`
          * **Combined queries:** `event_type:AUTH_ATTEMPT AND status:FAILURE`
          * **Phrase Search:** `message_raw:"unauthorized access"`
          * **Wildcard:** `user*` (will match UserA, UserB etc.)
          * **Search all documents:** `*:*` (shows first 10 results, useful to see what's indexed)
      * Type `exit` to quit the searcher.

### Optional: Simulating Live Log Streams

To see the anomaly detection and indexing working in a live streaming scenario (after initial indexing is complete):

1.  Keep your `log_processor.py` running in its terminal (from Phase 2).
2.  In the terminal where you ran `log_generator.py` (Phase 1), you can run it again. You might set `NUM_LOGS_TO_GENERATE = None` in `log_generator.py` to make it run indefinitely for a continuous stream.
    ```bash
    python log_generator.py
    ```
3.  Observe the `log_processor.py` terminal; it will start processing these newly generated logs and flagging anomalies in real-time.

-----

## Cleaning Up (Optional)

To remove all generated data (logs and index) and the virtual environment:

1.  **Deactivate your virtual environment** in all terminals where it's active:
    ```bash
    deactivate
    ```
2.  **Remove generated data folders:**
    ```bash
    rm -rf data
    rm -rf whoosh_index
    ```
3.  **Remove the virtual environment folder:**
    ```bash
    rm -rf venv
    ```

-----

## Project Structure

```
logguard/
├── data/
│   └── system_logs.log  # Generated log file (ignored by Git)
├── whoosh_index/        # Whoosh search index (ignored by Git)
├── venv/                # Python virtual environment (ignored by Git)
├── log_generator.py     # Script to generate synthetic log data
├── log_processor.py     # Script for log processing, ML anomaly detection, and indexing
├── log_searcher.py      # Script for interactive log searching
├── requirements.txt     # Python project dependencies
└── .gitignore           # Specifies files/directories to ignore in Git
└── README.md            # This project documentation
```

## Contact

For any questions or feedback, feel free to reach out:

  * **Akash Bais**
  * [Github](https://github.com/akashhbais)
  * Email: akashbais41203@gmail.com

<!-- end list -->

```
```
