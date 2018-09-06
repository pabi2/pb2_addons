"""
This script will click button Validate on Billing (draft)
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
Billing = connection.get_model('purchase.billing')

# Domain
dom = [('state', '=', 'draft')]

# Search Billing
billings = Billing.search_read(dom)

log_billing_ids = [[], []]
logger = log.setup_custom_logger('purchase_billing_act_validate')
logger.info('Start process')
logger.info('Total purchase billing: %s' % len(billings))
for billing in billings:
    try:
        Billing.mork_validate_billing([billing['id']])
        log_billing_ids[0].append(billing['id'])
        logger.info('Pass: %s' % billing['id'])
    except Exception as ex:
        log_billing_ids[1].append(billing['id'])
        logger.error('Fail: %s (reason: %s)' % (billing['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_billing_ids[0]),
             log_billing_ids[0] and ' %s' % str(tuple(log_billing_ids[0]))
             or '', len(log_billing_ids[1]),
             log_billing_ids[1] and ' %s' % str(tuple(log_billing_ids[1]))
             or '')
logger.info(summary)
logger.info('End process')
