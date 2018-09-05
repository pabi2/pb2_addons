"""
This method will click button confirm asset in assets
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
asset_codes = ['7440-028-0001-000000003']
dom = [('code', 'in', asset_codes)]

# Search Asset
assets = Asset.search_read(dom)

log_asset_codes = [[], []]
logger = log.setup_custom_logger('assets_act_confirm_asset')
logger.info('Start process')
logger.info('Total asset: %s' % len(assets))
for asset in assets:
    try:
        Asset.mork_validate([asset['id']])
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
