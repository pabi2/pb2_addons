"""
This method will click button compute in assets
"""
import sys
import os
try:
    asset_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(asset_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Asset = connection.get_model('account.asset')

# Domain
# excludes = [
#     '9100-001-0001-0002015-000',
#     '9100-001-0001-0001905-000',
#     '9100-001-0001-0001830-000',
# ]
dom = [('account_analytic_id', '=', False)]
# dom = [('code', 'in', excludes)]

# Search Asset
assets = Asset.search_read(dom, ['id', 'code'], limit=10000, order='id desc')

log_asset_codes = [[], []]
logger = log.setup_custom_logger('assets_act_create_matched_analytic')
logger.info('Start process')
logger.info('Total asset: %s' % len(assets))
for asset in assets:
    try:
        print asset['code']
        account_analytic_id = \
            Asset.fix_asset_account_analytic_id(asset['id'])
        log_asset_codes[0].append(asset['code'].encode('utf-8'))
        logger.info('Pass: %s' % asset['code'])
    except Exception as ex:
        log_asset_codes[1].append(asset['code'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (asset['code'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_asset_codes[0]),
             log_asset_codes[0] and ' %s' % str(tuple(log_asset_codes[0]))
             or '', len(log_asset_codes[1]),
             log_asset_codes[1] and ' %s' % str(tuple(log_asset_codes[1]))
             or '')
logger.info(summary)
logger.info('End process')
