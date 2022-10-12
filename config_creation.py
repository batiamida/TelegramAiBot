def create_config(file_name='conf.ini'):
    with open(file_name, 'w') as f:

        f.write('[DATABASE]\n')
        print("\nfor database\n")
        for (name, col) in [('host for database', 'host'), ('name of database', 'database'),
                            ('user', 'user'),
                            ('port to connect', 'port'),
                            ('password for your database', 'password')]:
            f.write(f'{col} = {input(f"write {col}: ")}\n')
        f.write('\n' * 3)

        f.write('[TELEGRAM]\n')
        f.write('name = my_account\n')
        print("\nfor telegram\n")
        for (name, col) in [('api id of your account', 'api_id'),
                            ('api hash of your account', 'api_hash')]:
            f.write(f'{col} = {input(f"write your {col}")}\n')