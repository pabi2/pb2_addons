"""
This method recalculate invoice plan of selected PO,
based on specific wizard params.
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

# Serach by name
po_names = ['PO18000535']
purchase_ids = Purchase.search([('name', 'in', po_names)])

# serach is_fin_lease, use_invoice_plan
# purchase_ids = Purchase.search([('use_invoice_plan', '=', True),
#                                 # ('is_fin_lease', '=', True),
#                                 ('state', '=', 'draft')])

print '--> PO Prepare Invoice Plan: %s' % len(purchase_ids)

for purchase_id in purchase_ids:
    install_start_date = datetime.now().strftime('%Y-%m-%d')
    Purchase.write([purchase_id], {'use_invoice_plan': True,
                                   'invoice_method': 'invoice_plan'})
    Purchase.mock_prepare_purchase_invoice_plan(
        purchase_id,
        installment_date=False,
        num_installment=3,
        installment_amount=False,
        interval=1, interval_type='month',
        invoice_mode='change_price',
        use_advance=True,
        advance_percent=15.0,
        use_deposit=False,
        advance_account='1106010005',
        use_retention=False)
    print '--> purchase_id processed: %s' % purchase_id
