"""
This script will click button Validate on Billing (draft)
Status: Done
"""
import openerplib
import ConfigParser
import os

conf_file = 'migration_remote.conf'


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
    protocal = config.get('server', 'protocal')
    connection = openerplib.get_connection(
        hostname=hostname, port=port, database=database, login=login,
        password=password, protocol=protocal, user_id=user_id)
    return connection


connection = get_connection(conf_file)
connection.check_login()
# Start your program ...

Billing = connection.get_model('purchase.billing')
billing_ids = Billing.search([('state', '=', 'draft')])
print '--> number of processing PO: %s' % len(billing_ids)
for billing_id in billing_ids:
    Billing.validate_billing([billing_id])
    print '--> processed for billing_id: %s' % billing_id
