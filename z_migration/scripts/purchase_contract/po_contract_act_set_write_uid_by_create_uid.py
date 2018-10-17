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
PurchaseContract = connection.get_model('purchase.contract')

# Domain
dom = []

# Search PO Contract
poc = PurchaseContract.search_read(dom)

log_po_names = [[], []]
logger = log.setup_custom_logger('po_contract_act_set_write_uid_by_create_uid')
logger.info('Start process')
logger.info('Total contract: %s' % len(poc))
try:
    # Update write uid with create_uid
    poc = [x['id'] for x in poc]
    PurchaseContract.mork_set_write_uid_by_create_uid(poc)
    logger.info('Updated: %s contracts' % len(poc))
except Exception as ex:
    logger.error('Fail: %s' % ex)
logger.info('End process')
