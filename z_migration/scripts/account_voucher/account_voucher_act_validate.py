"""
This method will click button validate in account voucher.
"""
import sys
import os
try:
    voucher_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(voucher_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Voucher = connection.get_model('account.voucher')

# Domain
dom = [('type', '=', 'receipt'), ('state', '=', 'draft')]

# Search Voucher
vouchers = Voucher.search_read(dom)

log_voucher_ids = [[], []]
logger = log.setup_custom_logger('account_voucher_act_validate')
logger.info('Start process')
logger.info('Total voucher: %s' % len(vouchers))
for voucher in vouchers:
    try:
        Voucher.mock_trigger_workflow([voucher['id']], 'proforma_voucher')
        log_voucher_ids[0].append(voucher['id'])
        logger.info('Pass ID: %s' % voucher['id'])
    except Exception as ex:
        log_voucher_ids[1].append(voucher['id'])
        logger.error('Fail ID: %s (reason: %s)' % (voucher['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_voucher_ids[0]),
             log_voucher_ids[0] and
             ' %s' % str(tuple(log_voucher_ids[0])) or '',
             len(log_voucher_ids[1]),
             log_voucher_ids[1] and
             ' %s' % str(tuple(log_voucher_ids[1])) or '')
logger.info(summary)
logger.info('End process')
