"""
This method will update create_uid follow force_done_reason in purchase order.
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
dom = [('force_done_reason', '!=', False)]

# Search PO
pos = PurchaseOrder.search_read(dom)

log_po_names = [[], []]
logger = log.setup_custom_logger('purchase_orders_act_update_create_uid')
logger.info('Start process')
logger.info('Total purchase order: %s' % len(pos))
for po in pos:
    try:
        # Update create uid
        PurchaseOrder.mork_update_create_uid([po['id']])

        # Clear force done reason
        PurchaseOrder.mork_clear_force_done_reason([po['id']])
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
