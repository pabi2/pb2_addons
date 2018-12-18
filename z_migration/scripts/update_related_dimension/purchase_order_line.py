"""
This method change all purchase.order.line dimension
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
POLine = connection.get_model('purchase.order.line')

# Updates list for all structure from -> to (by code)
#####################################################
d = {
    'section_id': {'101021': '101012',
                   'YYY': 'ZZZ'},
    'project_id': {'XXX': 'YYY'},
}
#####################################################

# Domain - get only relevant lines
dom = ['|', '|', '|', '|',
       ('section_id.code', 'in', d.get('section_id', {}).keys()),
       ('project_id.code', 'in', d.get('project_id', {}).keys()),
       ('invest_asset_id.code', 'in', d.get('invest_asset_id', {}).keys()),
       ('invest_construction_phase_id.code', 'in',
        d.get('invest_construction_phase_id', {}).keys()),
       ('personnel_costcenter_id.code', 'in',
        d.get('personnel_costcenter_id', {}).keys()), ]

# Search Budget
lines = POLine.search_read(dom, ['id'])

log_budget_names = [[], []]
logger = log.setup_custom_logger('Update Dimension for PO Lines')
logger.info('Start process')
logger.info('Total budget: %s' % len(lines))
for line in lines:
    try:
        Budget.mock_update_related_dimension(
            'purchase.order.line', [line['id']],
            'account_analytic_id', d)
        log_budget_names[0].append(line['id'])
        logger.info('Pass: %s' % line['id'])
    except Exception as ex:
        log_budget_names[1].append(line['id'])
        logger.error('Fail: %s (reason: %s)' % (line['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_budget_names[0]),
             log_budget_names[0] and ' %s' % str(tuple(log_budget_names[0]))
             or '', len(log_budget_names[1]),
             log_budget_names[1] and ' %s' % str(tuple(log_budget_names[1]))
             or '')
logger.info(summary)
logger.info('End process')
