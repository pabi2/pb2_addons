from locust import task, TaskSet
from OdooLocust import OdooLocust


class SellerTaskSet(TaskSet):
    @task(20)
    def create_so(self):
        prod_model = self.client.get_model('product.product')
        cust_model = self.client.get_model('res.partner')
        chart_model = self.client.get_model('chartfield.view')
        so_model = self.client.get_model('sale.order')
        partner_ids = cust_model.search([('search_key', 'ilike', '0004808')])
        prod_ids = prod_model.search([('name', 'ilike', 'Servo')])
        chart_ids = chart_model.search([('code', '=', '101009')])
        order_id = so_model.create({
            'partner_id': partner_ids[0],
            'order_line': [
                (0, 0, {'product_id': prod_ids[0],
                        'product_uom_qty': 1,
                        'name': 'test',
                        'chartfield_id': chart_ids[0],
                        }),
                (0, 0, {'product_id': prod_ids[0],
                        'product_uom_qty': 2,
                        'name': 'test',
                        'chartfield_id': chart_ids[0],
                        }), ],
        }, context={'order_type': 'sale_order'})
        so_model.action_button_confirm([order_id, ])


class Seller(OdooLocust):
    host = "127.0.0.1"
    database = "PABI2-1"
    min_wait = 100
    max_wait = 1000
    weight = 3
    task_set = SellerTaskSet
