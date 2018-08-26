"""
This method recalculate invoice plan of selected PO,
based on specific wizard params.
Status: Done
"""
import openerplib
import ConfigParser
import os
from datetime import datetime


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
# po_names = ['PO18000518']
# purchase_ids = Purchase.search([('name', 'in', po_names)])

# serach is_fin_lease, use_invoice_plan
purchase_ids = Purchase.search([('use_invoice_plan', '=', True),
                                ('is_fin_lease', '=', True),
                                ('state', '=', 'draft')])

print '--> number of processing PO: %s' % len(purchase_ids)

for purchase_id in purchase_ids:
    install_start_date = datetime.now().strftime('%Y-%m-%d')
    Purchase.generate_purchase_invoice_plan(purchase_id,
                                            install_start_date,
                                            num_installment=3,
                                            installment_amount=19800,
                                            interval=2, interval_type='month',
                                            invoice_mode='change_price',
                                            use_advance=False,
                                            advance_percent=False,
                                            use_deposit=False,
                                            advance_account=False,
                                            use_retention=False)
    print '--> purchase_id processed: %s' % purchase_id
