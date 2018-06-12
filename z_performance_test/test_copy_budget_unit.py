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
Section = connection.get_model('res.section')
section_ids = Section.search([])

for section_id in section_ids:
    data = {'creating_user_id': 1,
            'chart_view': 'unit_base',
            'section_id': section_id,
            'fiscalyear_id': 3,
            'control_ext_charge_only': True,
            'date_from': '2017-10-01',
            'date_to': '2018-09-30',
            'budget_expense_line_unit_base': [
                (0, 0, {'charge_type': 'external',
                        'fund_id': 1,
                        'activity_group_id': 162,
                        'm1': 1000000})
            ], }
    new_budget = Budget.create(data)
    print new_budget
    # print 'New Budget ID = %s' % new_budget
