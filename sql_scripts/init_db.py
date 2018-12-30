import subprocess
import os
from config.settings import DATABASE
from sql_scripts.pop_test_data import pop_data

CREATE_TABLES_SCRIPT = 'create_tables.sql'
ADD_FUNCTIONS_SCRIPT = 'create_functions.sql'


def run_script(script):
    status = subprocess.run(["psql", "-U", DATABASE['user'], "-f", script])
    if status.returncode != 0:
        print("Unable to connect to the database.")
        exit(status.returncode)


def main():
    os.environ['PGPASSWORD'] = DATABASE['password']
    run_script(CREATE_TABLES_SCRIPT)
    run_script(ADD_FUNCTIONS_SCRIPT)


if __name__ == "__main__":
    main()
    pop_data()
