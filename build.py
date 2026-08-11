"""Build script to package LocalAI Chat into a standalone Windows executable using PyInstaller."""
import subprocess
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build_executable():
    print("Building LocalAI-Chat.exe with PyInstaller...")
    spec_path = BASE_DIR / "LocalAI-Chat.spec"
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        str(spec_path)
    ]
    
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode == 0:
        exe_path = BASE_DIR / "dist" / "LocalAI-Chat.exe"
        print(f"\nBuild Successful! Standalone Executable created at:\n{exe_path}")
    else:
        print(f"\nBuild Failed with return code {result.returncode}")

if __name__ == "__main__":
    build_executable()
