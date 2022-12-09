import os


if __name__ == '__main__':
    os.system('pg_dump -U uni_project_user -d uni_database > uni_database.sql')