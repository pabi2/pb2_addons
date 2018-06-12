import openerplib
connection = openerplib.get_connection(
    hostname="pabi2o-test.intra.nstda.or.th",
    port=80,
    database="PABI2",
    login="admin",
    password="admin",
    protocol="jsonrpc",
    user_id=1)
# connection = openerplib.get_connection(
#     hostname="localhost",
#     port=8069,
#     database="PABI2_integration",
#     login="admin",
#     password="admin",
#     protocol="jsonrpc",
#     user_id=1)

connection.check_login()

# Copy, budget = CTRL/UNIT/18/200060 to all other sections

Budget = connection.get_model('account.budget')
budget_ids = Budget.search([])
Budget.budget_done(budget_ids)
