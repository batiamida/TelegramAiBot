import os



if __name__ == '__main__':
    os.system('psql -U uni_project_user -d uni_database < uni_database.sql')