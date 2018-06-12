import openerplib
connection = openerplib.get_connection(
    hostname="pabi2o-test.intra.nstda.or.th",
    port=80,
    database="PABI2",
    login="admin",
    password="admin",
    protocol="jsonrpc",
    user_id=1)
connection.check_login()
user_model = connection.get_model('res.users')
employee_model = connection.get_model('hr.employee')
org_model = connection.get_model('res.org')
user_ids = user_model.search([])
for user_id in user_ids:
    try:
        res = user_model.read(user_id, ['default_operating_unit_id',
                                        'employee_ids'])
        if not res['default_operating_unit_id']:
            if res['employee_ids']:
                # for ou_id
                emp_id = res['employee_ids'][0]
                res2 = employee_model.read(emp_id, ['org_id', 'org_ids'])
                org_id = res2['org_id'] and res2['org_id'][0] or False
                if not org_id:
                    continue
                res3 = org_model.read(org_id, ['operating_unit_id'])
                ou_id = res3.get('operating_unit_id', False) and \
                    res3['operating_unit_id'][0] or []
                user_model.write([user_id], {'default_operating_unit_id': ou_id,
                                             'operating_unit_ids': [(4, ou_id)]})
                # For ou_ids
                user_model.write([user_id], {'operating_unit_ids': [(4, ou_id)]})
                for org_id in res2.get('org_ids', []):
                    res3 = org_model.read(org_id, ['operating_unit_id'])
                    ou_id = res3['operating_unit_id'] and \
                        res3['operating_unit_id'][0] or []
                    user_model.write([user_id], {'operating_unit_ids': [(4, ou_id)]})
                print 'Done for user_id = %s' % user_id
    except Exception:
        pass
            # org_ids = [org_id]


    # org = rec.employee_ids and rec.employee_ids[0].org_id or False
    # orgs = rec.employee_ids and rec.employee_ids[0].org_ids or False
    # rec.default_operating_unit_id = org and org.operating_unit_id
    # rec.operating_unit_ids = False
    # if org and org.operating_unit_id:
    #     rec.operating_unit_ids |= org.operating_unit_id
    # if orgs and orgs.mapped('operating_unit_id'):
    #     rec.operating_unit_ids |= orgs.mapped('operating_unit_id')

# so_model.action_button_confirm([order_id, ])
