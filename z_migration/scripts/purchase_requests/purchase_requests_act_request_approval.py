"""
This method will click button request approval in purchase requests
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
PurchaseRequest = connection.get_model('purchase.request')

# Domain
pr_names = ['PR00132']
dom = [('name', 'in', pr_names)]

# Search PR
prs = PurchaseRequest.search_read(dom)

log_pr_names = [[], []]
logger = log.setup_custom_logger('purchase_requests_act_request_approval')
logger.info('Start process')
logger.info('Total purchase request: %s' % len(prs))
for pr in prs:
    try:
        PurchaseRequest.mork_button_to_approve([pr['id']])
        log_pr_names[0].append(pr['name'].encode('utf-8'))
        logger.info('Pass: %s' % pr['name'])
    except Exception as ex:
        log_pr_names[1].append(pr['name'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (pr['name'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_pr_names[0]),
             log_pr_names[0] and ' %s' % str(tuple(log_pr_names[0])) or '',
             len(log_pr_names[1]),
             log_pr_names[1] and ' %s' % str(tuple(log_pr_names[1])) or '')
logger.info(summary)
logger.info('End process')
