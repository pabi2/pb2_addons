"""
This method will click button validate in account invoice.
"""
import sys
import os
try:
    invoice_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(invoice_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Invoice = connection.get_model('account.invoice')

# Domain
dom = [('type', '=', 'out_invoice'), ('state', '=', 'draft')]

# Search Invoice
invs = Invoice.search_read(dom)

log_inv_ids = [[], []]
logger = log.setup_custom_logger('account_invoice_act_validate')
logger.info('Start process')
logger.info('Total invoice: %s' % len(invs))
for inv in invs:
    try:
        Invoice.mock_trigger_workflow([inv['id']], 'invoice_open')
        log_inv_ids[0].append(inv['id'])
        logger.info('Pass ID: %s' % inv['id'])
    except Exception as ex:
        log_inv_ids[1].append(inv['id'])
        logger.error('Fail ID: %s (reason: %s)' % (inv['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_inv_ids[0]),
             log_inv_ids[0] and ' %s' % str(tuple(log_inv_ids[0])) or '',
             len(log_inv_ids[1]),
             log_inv_ids[1] and ' %s' % str(tuple(log_inv_ids[1])) or '')
logger.info(summary)
logger.info('End process')
