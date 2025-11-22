import os
from datetime import datetime

# Root paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(BASE_DIR, "..", "datasets", "BMW sales data (2020-2024).xlsx")
REPORTS_ROOT = os.path.join(BASE_DIR, "..", "reports")

# Make a timestamped folder for each run
def get_run_report_dir():
    timestamp = datetime.now().strftime("run_%Y_%m_%d_%H_%M_%S")
    run_dir = os.path.join(REPORTS_ROOT, timestamp)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(os.path.join(run_dir, "figures"), exist_ok=True)
    return run_dir
