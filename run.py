
import subprocess
def run_shell_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully ran: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error while running {command}: {e}")


run_shell_command('python manage.py runserver')
