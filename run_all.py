# Runs the whole pipeline in order: database -> SQL analysis -> models
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
steps = ["01_build_database.py", "02_sql_analysis.py", "03_crop_recommender.py", "04_yield_model.py"]

for step in steps:
    print(f"\n===== Running {step} =====")
    result = subprocess.run([sys.executable, str(BASE / "src" / step)])
    if result.returncode != 0:
        print(f"{step} failed. Please check the error above.")
        sys.exit(1)

print("\nAll done. Now start the app with:  streamlit run app.py")
