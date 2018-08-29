"""
This method will click create work acceptance in purchase order
"""
import openerplib
import ConfigParser
import os

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
    protocal = config.get('server', 'protocal')
    connection = openerplib.get_connection(
        hostname=hostname, port=port, database=database, login=login,
        password=password, protocol=protocal, user_id=user_id)
    return connection


connection = get_connection(conf)
connection.check_login()

# Start your program ...
po_model = connection.get_model('purchase.order')
create_acceptance_model = \
    connection.get_model('create.purchase.work.acceptance')
acceptance_model = connection.get_model('purchase.work.acceptance')
acceptance_line_model = connection.get_model('purchase.work.acceptance.line')

# domain follow state
# dom = [('order_type', '=', 'purchase_order'), ('state', '=', 'approved')]

# domain follow purchase id
# po_ids = [1200]
# dom = [('id', 'in', po_ids)]

# domain follow purchase name
po_names = ['PO18001189']
dom = [('name', 'in', po_names)]

# Search puchase by domain as defined
pos = po_model.search_read(dom)

pass_po_ids, pass_po_names = [], []
error_po_ids, error_po_names = [], []
print ":: Start process ::"
print "Total purchase order : %s" % len(pos)
print "Status  PO Name"
for po in pos:
    try:
        ctx = {'active_id': po['id'], 'active_ids': [po['id']]}
        fields = [
            'acceptance_line_ids', 'date_scheduled_end', 'is_invoice_plan',
            'select_invoice_plan', 'date_receive', 'order_id',
            'date_contract_end']
        create_acceptance = \
            create_acceptance_model.default_get(fields, context=ctx)
        create_acceptance_id = \
            create_acceptance_model.create(create_acceptance, context=ctx)
        create_acceptance_model \
            .mork_action_create_work_acceptance(
                [create_acceptance_id], context=ctx)
        acceptance_ids = acceptance_model.search([('order_id', '=', po['id'])])
        for acceptance_id in acceptance_ids:
            acceptance_lines = acceptance_line_model.search_read(
                [('acceptance_id', '=', acceptance_id)])
            for acceptance_line in acceptance_lines:
                acceptance_line_model.write(
                    [acceptance_line['id']],
                    {'to_receive_qty': acceptance_line['balance_qty']})
        pass_po_ids.append(po['id'])
        pass_po_names.append(po['name'].encode('utf-8'))
        print "Pass : %s" % po['name']
    except Exception:
        error_po_ids.append(po['id'])
        error_po_names.append(po['name'].encode('utf-8'))
        print "Fail : %s" % po['name']

# Summary pass and fail po
summary = "\nSummary\nPass : %s" % len(pass_po_ids)
if pass_po_ids:
    summary += "\npo ids : \n%s\npo names : \n%s" \
               % (pass_po_ids, pass_po_names)
summary += "\nFail : %s" % len(error_po_ids)
if error_po_ids:
    summary += "\npo ids : \n%s\npo names : \n%s" \
               % (error_po_ids, error_po_names)
print summary
print ":: End process ::"
