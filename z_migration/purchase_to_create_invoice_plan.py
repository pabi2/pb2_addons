"""
Describe this module here...
 - xxx
 - yyy
"""
import openerplib
import ConfigParser
import os


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
    connection = openerplib.get_connection(
        hostname=hostname, port=port, database=database, login=login,
        password=password, protocol="jsonrpc", user_id=user_id)
    return connection


connection = get_connection('migration.conf')
connection.check_login()

# Start your program ...

# Expense = connection.get_model('hr.expense.expense')
# expense_ids = Expense.search([('number', '=', 'EX18000001')])
# expense_id = Expense.copy(expense_ids[0], {})
# Expense.signal_workflow([expense_id], 'confirm')
# ctx = {'active_model': 'hr.expense.expense', 'active_id': expense_id}
# Expense.action_accept_to_paid([expense_id], context=ctx)
