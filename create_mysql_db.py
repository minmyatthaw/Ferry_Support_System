"""Create the MySQL database defined in .env if it does not exist."""

import os
import sys
from pathlib import Path

import MySQLdb
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', '')
host = os.getenv('MYSQL_HOST', '127.0.0.1')
port = int(os.getenv('MYSQL_PORT', '3306'))
database = os.getenv('MYSQL_DATABASE', 'django_db')

try:
    connection = MySQLdb.connect(
        host=host,
        user=user,
        passwd=password,
        port=port,
        charset='utf8mb4',
    )
except MySQLdb.Error as exc:
    print(f'Could not connect to MySQL: {exc}')
    print('Update MYSQL_PASSWORD (and other MYSQL_* values) in .env, then run again.')
    sys.exit(1)

with connection.cursor() as cursor:
    cursor.execute(
        f'CREATE DATABASE IF NOT EXISTS `{database}` '
        'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
    )
    connection.commit()

connection.close()
print(f'Database `{database}` is ready.')
