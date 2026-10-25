"""Regenerate the final audit summary from checks/results."""
from pathlib import Path
import runpy,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'checks'))
runpy.run_path(str(R/'checks/report.py'),run_name='__main__')
