"""
This method click create invoice button (for case invoice plan),
Status: Done
"""
from datetime import datetime
import openerplib
import ConfigParser
import os


# conf_file = 'migration_remote.conf'
conf_file = 'migration.conf'


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
Purchase = connection.get_model('purchase.order')

# ==================== SEARCH ====================
# Serach by name
po_names = ['PO18000528']
purchase_ids = Purchase.search([('name', 'in', po_names)])

# serach is_fin_lease, use_invoice_plan
# purchase_ids = Purchase.search([('use_invoice_plan', '=', True),
#                                 # ('is_fin_lease', '=', True),
#                                 ('state', '=', 'draft')])

print '--> PO Create Invoices: %s' % len(purchase_ids)

for purchase_id in purchase_ids:
    print '--> purchase_id: %s' % purchase_id
    Purchase.mock_action_invoice_create([purchase_id])
