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
Move = connection.get_model('account.move')

# Domain - Journal = Depre
dom = [('journal_id', '=', 11), ('state', '=', 'draft')]

# Search Invoice
moves = Move.search_read(dom, ['id'], order='id asc')

log_inv_ids = [[], []]
logger = log.setup_custom_logger('account_move_post')
logger.info('Start process')
logger.info('Total invoice: %s' % len(moves))
for m in moves:
    try:
        # Update Tax
        Move.post([m['id']])
        log_inv_ids[0].append(m['id'])
        logger.info('Pass ID: %s' % m['id'])
    except Exception as ex:
        log_inv_ids[1].append(m['id'])
        logger.error('Fail ID: %s (reason: %s)' % (m['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_inv_ids[0]),
             log_inv_ids[0] and ' %s' % str(tuple(log_inv_ids[0])) or '',
             len(log_inv_ids[1]),
             log_inv_ids[1] and ' %s' % str(tuple(log_inv_ids[1])) or '')
logger.info(summary)
logger.info('End process')
