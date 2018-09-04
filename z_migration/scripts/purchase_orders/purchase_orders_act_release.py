"""
This method will click button release in purchase order
"""
import sys
import os
try:
    purchase_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(purchase_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
PurchaseOrder = connection.get_model('purchase.order')

# Domain
po_names = ['PO18001191', 'PO18001192', 'PO18001193']
dom = [('name', 'in', po_names)]

# Search PO
pos = PurchaseOrder.search_read(dom)

log_po_names = [[], []]
logger = log.setup_custom_logger('purchase_orders_act_release')
logger.info('Start process')
logger.info('Total purchase order: %s' % len(pos))
for po in pos:
    try:
        PurchaseOrder.mock_trigger_workflow([po['id']], 'purchase_approve')
        log_po_names[0].append(po['name'].encode('utf-8'))
        logger.info('Pass: %s' % po['name'])
    except Exception as ex:
        log_po_names[1].append(po['name'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (po['name'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_po_names[0]),
             log_po_names[0] and ' %s' % str(tuple(log_po_names[0])) or '',
             len(log_po_names[1]),
             log_po_names[1] and ' %s' % str(tuple(log_po_names[1])) or '')
logger.info(summary)
logger.info('End process')
