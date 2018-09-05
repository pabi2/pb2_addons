# -*- coding: utf-8 -*-
"""
For only connection. You can change config file name from keyword
"Config file name" in comment line, ex: migration.conf.
In config file has hostname, port, database, login, password, user_id and
protocal.

Prepare config file
1. migration_remote.conf (For server pre-production).
2. migration.conf (For server localhost).
"""
import openerplib
import ConfigParser
import os

# Config file name
conf = 'migration.conf'


def get_connection(config_file):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = '%s/%s' % (file_dir, config_file)
    config = ConfigParser.ConfigParser()
    config.readfp(open(file_path))
    hostname = config.get('server', 'hostname')
    port = int(config.get('server', 'port'))
    database = config.get('server', 'database')
    login = config.get('server', 'login')
    password = config.get('server', 'password')
    user_id = int(config.get('server', 'user_id'))
    protocol = config.get('server', 'protocol')
    connection = openerplib.get_connection(
        hostname=hostname, port=port, database=database, login=login,
        password=password, protocol=protocol, user_id=user_id)
    return connection


connection = get_connection(conf)
connection.check_login()
