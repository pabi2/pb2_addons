"""
This method will click button activate in budgets
"""
import sys
import os
try:
    budget_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(budget_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Budget = connection.get_model('account.budget')

# Domain
budget_names = ['CTRL/UNIT/18/301060', 'CTRL/PERSONNEL/19/NSTDA']
dom = [('name', 'in', budget_names)]

# Search Budget
budgets = Budget.search_read(dom)

log_budget_names = [[], []]
logger = log.setup_custom_logger('budgets_act_activate')
logger.info('Start process')
logger.info('Total budget: %s' % len(budgets))
for budget in budgets:
    try:
        Budget.mork_budget_done([budget['id']])
        log_budget_names[0].append(budget['name'].encode('utf-8'))
        logger.info('Pass: %s' % budget['name'])
    except Exception as ex:
        log_budget_names[1].append(budget['name'].encode('utf-8'))
        logger.error('Fail: %s (reason: %s)' % (budget['name'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_budget_names[0]),
             log_budget_names[0] and ' %s' % str(tuple(log_budget_names[0]))
             or '', len(log_budget_names[1]),
             log_budget_names[1] and ' %s' % str(tuple(log_budget_names[1]))
             or '')
logger.info(summary)
logger.info('End process')
