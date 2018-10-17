import openerplib
import time
connection = openerplib.get_connection(
    hostname="pabi2o.nstda.or.th",
    port=443,
    database="PABI2_MIG",
    login="admin",
    password="password",
    protocol="xmlrpcs",
    user_id=1)
# connection = openerplib.get_connection(
#     hostname="localhost",
#     port=8069,
#     database="PABI2",
#     login="admin",
#     password="pabi2",
#     protocol="jsonrpc",
#     user_id=1)

connection.check_login()

Asset = connection.get_model('account.asset')
asset_ids = Asset.search([('code', '=', '6120-003-0001-000000001')])
begin = time.time()


def execute(start, i):
    asset_id = Asset.copy(asset_ids[0], {'name': str(start),
                                         'code': str(start)})
    Asset.compute_depreciation_board([asset_id])
    Asset.validate([asset_id])
    end = time.time()
    print '---------> Count = %s, Time = %s, Accum Time = %s' % \
        (i, (end-start), (end-begin))


for i in range(100000):
    start = time.time()
    try:
        execute(start, i)
    except Exception:
        pass
