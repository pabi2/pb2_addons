import openerplib
connection = openerplib.get_connection(
    hostname="pabi2o-test.intra.nstda.or.th",
    port=80,
    database="PABI2",
    login="admin",
    password="pabi2",
    protocol="jsonrpc",
    user_id=1)
# connection = openerplib.get_connection(
#     hostname="localhost",
#     port=8069,
#     database="PABI2_int11",
#     login="admin",
#     password="pabi2",
#     protocol="jsonrpc",
#     user_id=1)

connection.check_login()

Project = connection.get_model('res.project')
Budget = connection.get_model('account.budget')
BudgetPlan = connection.get_model('res.project.budget.plan')
# project_ids = Project.search([('budget_plan_ids', '=', False)])
# print project_ids
# Create budget plan line
# for project in project_ids:
#     data = {'project_id': project,
#             'budget_method': 'expense',
#             'fiscalyear_id': 3,
#             'charge_type': 'external',
#             'activity_group_id': 162,
#             'm1': 10000000, }
#     new_budget = BudgetPlan.create(data)
#     print new_budget

# budget_ids = Budget.search([('chart_view', '=', 'project_base')])
# # Synce
# for budget in budget_ids:
#     print budget
#     res = Budget.sync_budget_my_project([budget])


count = BudgetPlan.search_count([('synced', '=', False)])
print 'Remaining = %s' % count
plan_ids = BudgetPlan.search([('synced', '=', False)])
project_ids = []
for plan in plan_ids:
    print plan
    try:
        BudgetPlan.release_budget(plan, 10000000)
    except Exception:
        pass
