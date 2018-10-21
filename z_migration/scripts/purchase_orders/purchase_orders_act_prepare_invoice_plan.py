"""
This method recalculate invoice plan of selected PO,
based on specific wizard params.
Status: Done
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
po_names = ['PO18001215']
dom = [('name', 'in', po_names)]

# Search PO
pos = PurchaseOrder.search_read(dom)

log_po_names = [[], []]
logger = log.setup_custom_logger('purchase_orders_act_prepare_invoice_plan')
logger.info('Start process')
logger.info('Total purchase order: %s' % len(pos))
for po in pos:
    try:
        PurchaseOrder.write([po['id']], {'use_invoice_plan': True,
                                         'invoice_method': 'invoice_plan'})
        PurchaseOrder.mock_prepare_purchase_invoice_plan(
            po['id'],
            installment_date=po['installment_date'],
            num_installment=po['num_installment'],
            installment_amount=False,
            interval=po['interval'], interval_type=po['doc_no'],
            invoice_mode=po['invoice_mode'],
            use_advance=False,
            advance_percent=0.0,
            use_deposit=False,
            advance_account=False,
            use_retention=False)
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
