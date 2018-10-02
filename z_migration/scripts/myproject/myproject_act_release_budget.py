"""
This method will click release budget of myproject in current year
"""
import sys
import os
try:
    myproject_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(myproject_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Project = connection.get_model('res.project')

# Domain
pj_codes = ['P1350176']
dom = [('code', 'in', pj_codes)]

# Search Project
pjs = Project.search_read(dom)

log_pj_codes = [[], []]
logger = log.setup_custom_logger('myproject_act_release_budget')
logger.info('Start process')
logger.info('Total project: %s' % len(pjs))
for pj in pjs:
    try:
        Project.mork_release_budget([pj['id']])
        log_pj_codes[0].append(pj['code'].encode('utf-8'))
        logger.info('Pass: %s' % pj['code'])
    except Exception as ex:
        log_pj_codes[1].append(pj['code'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (pj['code'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_pj_codes[0]),
             log_pj_codes[0] and ' %s' % str(tuple(log_pj_codes[0])) or '',
             len(log_pj_codes[1]),
             log_pj_codes[1] and ' %s' % str(tuple(log_pj_codes[1])) or '')
logger.info(summary)
logger.info('End process')
