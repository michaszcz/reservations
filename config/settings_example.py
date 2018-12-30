from config import consts

SECRET = '$2b$12$h44grQgk2gyIRtY2cRellu'
DATABASE = {
    'host': 'localhost',
    'dbname': 'postgres',
    'user': 'username',
    'password': 'my_password',
    'options': f'-c search_path={consts.SCHEMA}'
}
