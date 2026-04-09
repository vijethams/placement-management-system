import subprocess
import os

def run_git_init():
    try:
        result = subprocess.run(["git", "init"], capture_output=True, text=True, check=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except Exception as e:
        print("ERROR:", str(e))

if __name__ == "__main__":
    run_git_init()
