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
#     database="PABI2_int7",
#     login="admin",
#     password="pabi2",
#     protocol="jsonrpc",
#     user_id=1)

connection.check_login()

BudgetPlan = connection.get_model('res.project.budget.plan')
Project = connection.get_model('res.project')

plan_ids = BudgetPlan.search([('fiscalyear_id.name', '=', '2018')])
project_ids = []
for plan in plan_ids:
    # Only copy if no fiscaly year 2019 for this project yet
    res = BudgetPlan.read([plan], ['project_id'])
    project_id = res[0]['project_id'][0]
    fy_2019 = 4
    plan_ids = BudgetPlan.search([('fiscalyear_id', '=', fy_2019),
                                  ('project_id', '=', project_id)])
    if not plan_ids:
        new_plan = BudgetPlan.copy(plan, {'fiscalyear_id': fy_2019})
        res = Project.sync_budget_control([project_id])
        print 'New budget plan id: %s' % new_plan
    else:
        print 'Budget plan already exist for %s' % plan_ids[0]
