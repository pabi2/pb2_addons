"""
This method will click button approve in project construction.
"""
import sys
import os
try:
    project_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(project_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
ProjectConstruction = connection.get_model('res.invest.construction')

# Domain
pc_codes = ['C-18-111']
dom = [('code', 'in', pc_codes)]

# Search Project Construction
pcs = ProjectConstruction.search_read(dom)

log_pc_codes = [[], []]
logger = log.setup_custom_logger('project_construction_act_approve')
logger.info('Start process')
logger.info('Total project construction: %s' % len(pcs))
for pc in pcs:
    try:
        ProjectConstruction.mork_action_approve([pc['id']])
        log_pc_codes[0].append(pc['code'].encode('utf-8'))
        logger.info('Pass: %s' % pc['code'])
    except Exception as ex:
        log_pc_codes[1].append(pc['code'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (pc['code'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_pc_codes[0]),
             log_pc_codes[0] and ' %s' % str(tuple(log_pc_codes[0])) or '',
             len(log_pc_codes[1]),
             log_pc_codes[1] and ' %s' % str(tuple(log_pc_codes[1])) or '')
logger.info(summary)
logger.info('End process')
