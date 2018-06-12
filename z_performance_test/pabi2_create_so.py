import openerplib
connection = openerplib.get_connection(
    hostname="pabi2o-test.intra.nstda.or.th",
    port=443,
    database="PABI2",
    login="admin",
    password="admin",
    protocol="jsonrpcs",
    user_id=1)
connection.check_login()
partner_model = connection.get_model('res.partner')
so_model = connection.get_model('sale.order')
chart_model = connection.get_model('chartfield.view')
product_model = connection.get_model('product.product')
partner_ids = partner_model.search([('search_key', 'ilike', '0004808')])
product_ids = product_model.search([('name', 'ilike', 'Servo')])
chart_ids = chart_model.search([('code', '=', '101009')])
order_id = so_model.create({
    'partner_id': partner_ids[0],
    'order_line': [
        (0, 0, {'product_id': product_ids[0],
                'product_uom_qty': 1,
                'name': 'test',
                'chartfield_id': chart_ids[0]}),
        ],
    }, context={'order_type': 'sale_order'})

# so_model.action_button_confirm([order_id, ])
