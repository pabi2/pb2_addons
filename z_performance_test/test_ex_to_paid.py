import openerplib
connection = openerplib.get_connection(
    hostname="pabi2o-test.intra.nstda.or.th",
    port=80,
    database="PABI2_ptest",
    login="admin",
    password="admin",
    protocol="jsonrpc",
    user_id=1)
# connection = openerplib.get_connection(
#     hostname="localhost",
#     port=8069,
#     database="PABI2_int3",
#     login="admin",
#     password="admin",
#     protocol="jsonrpc",
#     user_id=1)

connection.check_login()

Expense = connection.get_model('hr.expense.expense')
expense_ids = Expense.search([('number', '=', 'EX18000001')])
expense_id = Expense.copy(expense_ids[0], {})
Expense.signal_workflow([expense_id], 'confirm')
ctx = {'active_model': 'hr.expense.expense', 'active_id': expense_id}
Expense.action_accept_to_paid([expense_id], context=ctx)
