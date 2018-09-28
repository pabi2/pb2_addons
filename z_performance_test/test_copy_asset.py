import openerplib
import time
# connection = openerplib.get_connection(
#     hostname="pabi2o-test.intra.nstda.or.th",
#     port=80,
#     database="PABI2_ptest",
#     login="admin",
#     password="admin",
#     protocol="jsonrpc",
#     user_id=1)
connection = openerplib.get_connection(
    hostname="localhost",
    port=8069,
    database="PABI2",
    login="admin",
    password="pabi2",
    protocol="jsonrpc",
    user_id=1)

connection.check_login()

Asset = connection.get_model('account.asset')
asset_ids = Asset.search([('name', '=', 'NUI')])
begin = time.time()
for i in range(100000):
    start = time.time()
    asset_id = Asset.copy(asset_ids[0], {'name': 'X-%s' % i,
                                         'code': 'X-%s' % i})
    Asset.compute_depreciation_board([asset_id])
    Asset.validate([asset_id])
    end = time.time()
    print '---------> Count = %s, Time = %s, Accum Time = %s' % \
        (i, (end-start), (end-begin))
