"""
This method will click button submit in project construction phase.
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
ProjectPhase = connection.get_model('res.invest.construction.phase')

# Domain
pcp_codes = ['C-18-082-01']
dom = [('code', 'in', pcp_codes)]

# Search Project Construction Phase
pcps = ProjectPhase.search_read(dom, context={'active_test': 0})

log_pcp_codes = [[], []]
logger = log.setup_custom_logger('project_construction_phase_act_submit')
logger.info('Start process')
logger.info('Total project construction phase: %s' % len(pcps))
for pcp in pcps:
    try:
        ProjectPhase.mork_action_submit([pcp['id']])
        log_pcp_codes[0].append(pcp['code'].encode('utf-8'))
        logger.info('Pass: %s' % pcp['code'])
    except Exception as ex:
        log_pcp_codes[1].append(pcp['code'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (pcp['code'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_pcp_codes[0]),
             log_pcp_codes[0] and ' %s' % str(tuple(log_pcp_codes[0])) or '',
             len(log_pcp_codes[1]),
             log_pcp_codes[1] and ' %s' % str(tuple(log_pcp_codes[1])) or '')
logger.info(summary)
logger.info('End process')
