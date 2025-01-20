import os

# Define the directory of the Python file
project_dir = r"C:\Users\pc\Desktop\secure_shop"
os.chdir(project_dir)

# Define the Python file to lint
file_to_lint = "main.py"

# Commands for linting
commands = [
    f"flake8 {file_to_lint} > flake8_report.txt",
    f"pylint {file_to_lint} > pylint_report.txt",
    f"black --check {file_to_lint} > black_report.txt 2>&1"
]

# Execute each command and report status
for cmd in commands:
    print(f"Running: {cmd}")
    exit_code = os.system(cmd)
    if exit_code != 0:
        print(f"Command failed: {cmd}")

print("\nLinting complete. Reports generated in the folder:")
print(f"- {project_dir}")
