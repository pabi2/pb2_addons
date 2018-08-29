"""
This method will click button receive product in purchase order
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
    connection = openerplib.get_connection(
        hostname=hostname, port=port, database=database, login=login,
        password=password, protocol="jsonrpc", user_id=user_id)
    return connection


connection = get_connection(conf)
connection.check_login()

# Start your program ...
po_model = connection.get_model('purchase.order')
picking_model = connection.get_model('stock.picking')
acceptance_model = connection.get_model('purchase.work.acceptance')
transfer_details_model = connection.get_model('stock.transfer_details')
group_model = connection.get_model('procurement.group')
data_model = connection.get_model('ir.model.data')

# domain follow state
# dom = [('order_type', '=', 'purchase_order'), ('state', '=', 'approved')]

# domain follow purchase id
# po_ids = [1200]
# dom = [('id', 'in', po_ids)]

# domain follow purchase name
po_names = ['PO18001165']
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
        cod_pay_term_id = data_model.get_object_reference(
            'purchase_cash_on_delivery', 'cash_on_delivery_payment_term')[1]
        if po['invoice_method'] == 'order' and \
           po['payment_term_id'][0] == cod_pay_term_id:
            if not po['invoiced'] or \
                False in [x.state == 'paid' and True or False
                          for x in po['invoice_ids']]:
                x = 1/0
        # --
        group_ids = group_model.search([('name', '=', po['name'])])
        picking_ids = picking_model.search([('group_id', 'in', group_ids)])
        for picking_id in picking_ids:
            picking = picking_model.search_read(
                [('id', '=', picking_id)])[0]
            # Save Work Acceptance
            dom_acceptance = [
                ('state', 'not in', ('done', 'cancel')),
                ('order_id', '=', picking['origin'])]
            acceptance_ids = acceptance_model.search(dom_acceptance)
            if acceptance_ids:
                picking_model.write(
                    [picking_id], {'acceptance_id': acceptance_ids[0]})
            detail_id = \
                picking_model.do_enter_transfer_details([picking_id])['res_id']
            transfer_details_model.do_detailed_transfer(detail_id)
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
