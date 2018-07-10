import openerplib

# Groups to assign
groups = [
    'pabi_base.group_nstda_admin_business',
    'pabi_base.group_budget_manager',
]

# User to assign
users = [
    'admin',
    '005859',
]

# ==============================================================
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
User = connection.get_model('res.users')
Data = connection.get_model('ir.model.data')

group_ids = []
for grp in groups:
    g = grp.split('.')
    res = Data.get_object_reference(g[0], g[1])
    print res
    group_ids.append((4, res[1]))

user_ids = User.search([('login', 'in', users)])
for uid in user_ids:
    User.write([uid], {'groups_id': group_ids})
    print 'Assigned groups: %s for user: %s' % (groups, uid)
