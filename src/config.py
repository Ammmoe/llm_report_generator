import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)  # one directory above the script location

DATASET_PATH = os.path.join(PARENT_DIR, "datasets", "BMW sales data (2020-2024).xlsx")
REPORTS_ROOT = os.path.join(PARENT_DIR, "reports")

# Make a timestamped folder for each run
def get_run_report_dir():
    timestamp = datetime.now().strftime("run_%Y_%m_%d_%H_%M_%S")
    run_dir = os.path.join(REPORTS_ROOT, timestamp)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(os.path.join(run_dir, "figures"), exist_ok=True)
    return run_dir
