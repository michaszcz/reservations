import bcrypt
from config.settings import SECRET


def hash_password(raw_pass):
    return bcrypt.hashpw(raw_pass.encode('utf-8'), SECRET)


def check_password(raw_pass, hashed):
    return bcrypt.checkpw(raw_pass.encode('utf-8'), hashed)
