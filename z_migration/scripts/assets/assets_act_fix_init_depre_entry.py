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
AssetLine = connection.get_model('account.asset.line')

# Domain
dom = [('type', '=', 'depreciate'),
       ('init_entry', '=', True),
       ('move_check', '=', False)]

# Search Asset
depre_lines = AssetLine.search_read(dom, limit=1)
log_asset_codes = [[], []]
logger = log.setup_custom_logger('assets_act_fix_init_depre_entry')
logger.info('Start process')
logger.info('Total depre_lines: %s' % len(depre_lines))
for depre in depre_lines:
    try:
        asset_id = depre['asset_id'][0]
        Asset.create_depre_init_entry_on_migration([asset_id])
        log_asset_codes[0].append(asset_id)
        logger.info('Pass: %s' % asset_id)
    except Exception as ex:
        log_asset_codes[1].append(asset_id)
        logger.error('Fail: %s (reason: %s)' % (asset_id, ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_asset_codes[0]),
             log_asset_codes[0] and ' %s' % str(tuple(log_asset_codes[0]))
             or '', len(log_asset_codes[1]),
             log_asset_codes[1] and ' %s' % str(tuple(log_asset_codes[1]))
             or '')
logger.info(summary)
logger.info('End process')
