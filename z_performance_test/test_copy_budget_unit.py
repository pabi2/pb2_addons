import openerplib
# connection = openerplib.get_connection(
#     hostname="pabi2o-test.intra.nstda.or.th",
#     port=80,
#     database="PABI2",
#     login="admin",
#     password="admin",
#     protocol="jsonrpc",
#     user_id=1)
connection = openerplib.get_connection(
    hostname="localhost",
    port=8069,
    database="PABI2_integration",
    login="admin",
    password="admin",
    protocol="jsonrpc",
    user_id=1)

connection.check_login()

# Copy, budget = CTRL/UNIT/18/200060 to all other sections

Budget = connection.get_model('account.budget')
Section = connection.get_model('res.section')
section_ids = Section.search([('id', '!=', 1)])
for section_id in section_ids:
    new_budget = Budget.copy(1, {'section_id': section_id,
                                 'budget_expense_line_project_base': [],
                                 'budget_expense_line_unit_base': [],})
    print new_budget
    # print 'New Budget ID = %s' % new_budget
