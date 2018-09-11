import openerplib
import time
# connection = openerplib.get_connection(
#     hostname="pabi2o-test.intra.nstda.or.th",
#     port=80,
#     database="PABI2_ptest",
#     login="admin",
#     password="admin",
#     protocol="jsonrpc",
#     user_id=1)
connection = openerplib.get_connection(
    hostname="localhost",
    port=8069,
    database="PABI2",
    login="admin",
    password="pabi2",
    protocol="jsonrpc",
    user_id=1)

connection.check_login()

PO = connection.get_model('purchase.order')
po_ids = PO.search([('name', '=', 'PO18001394')])
count = 1000
begin = time.time()
for i in range(1000):
    start = time.time()
    po_id = PO.copy(po_ids[0], {})
    PO.action_po_to_invoice([po_id], context={'bypass_due_date_check': True,
                                              'active_ids': [po_id]})
    end = time.time()
    print '---------> Count = %s, Time = %s, Accum Time = %s' % \
        (i, (end-start), (end-begin))
