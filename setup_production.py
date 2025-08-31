import os
import subprocess
import sys

def run_command(command):
    """Runs a shell command and prints the output."""
    print(f"\n--- Running: {' '.join(command)} ---")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        if process.returncode != 0:
            print(f"--- ERROR: Command failed with return code {process.returncode} ---")
            sys.exit(process.returncode)
        else:
            print(f"--- SUCCESS: Command finished. ---")
    except Exception as e:
        print(f"--- FATAL ERROR executing command: {e} ---")
        sys.exit(1)

def ensure_log_directory():
    """Ensures the log directory exists and is writable."""
    log_dir = "/home1/oraaghco/oraagh/logs"
    try:
        os.makedirs(log_dir, exist_ok=True)
        os.chmod(log_dir, 0o775)
        print(f"--- SUCCESS: Log directory {log_dir} ensured. ---")
    except Exception as e:
        print(f"--- ERROR: Failed to create log directory {log_dir}: {e} ---")
        sys.exit(1)

def main():
    """Runs all necessary setup commands for production deployment, including superuser creation."""
    project_path = os.path.dirname(os.path.abspath(__file__))
    # Set PYTHONPATH to ensure project modules are found
    os.environ['PYTHONPATH'] = project_path + os.pathsep + os.environ.get('PYTHONPATH', '')

    # Ensure we are in the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 0. Ensure log directory exists to avoid logging errors
    ensure_log_directory()

    # 1. Install dependencies
    run_command(['pip', 'install', '-r', 'requirements_production.txt'])

    # 2. Run database migrations
    run_command(['python', 'manage_production.py', 'migrate'])

    # 3. Collect static files
    run_command(['python', 'manage_production.py', 'collectstatic', '--noinput'])

    # 4. Create superuser
    print("\n--- Creating superuser ---")
    os.environ['DJANGO_SUPERUSER_USERNAME'] = 'sameer321'
    os.environ['DJANGO_SUPERUSER_EMAIL'] = 'sameergul72462@gmail.com'
    os.environ['DJANGO_SUPERUSER_PASSWORD'] = 'Silent12.'
    run_command(['python', 'manage_production.py', 'createsuperuser', '--noinput'])

    print("\n" + "*"*50)
    print("Automated setup complete!")
    print("Superuser created with username: sameer321")
    print("You can now log in to the Django admin panel.")
    print("*"*50 + "\n")

if __name__ == "__main__":
    main()