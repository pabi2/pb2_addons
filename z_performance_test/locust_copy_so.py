from locust import task, TaskSet
from OdooLocust import OdooLocust


class SellerTaskSet(TaskSet):
    @task(20)
    def copy_so(self):
        # prod_model = self.client.get_model('product.product')
        # cust_model = self.client.get_model('res.partner')
        # chart_model = self.client.get_model('chartfield.view')
        so_model = self.client.get_model('sale.order')
        sale_ids = so_model.search([('name', '=', 'SO18000001')])
        order_id = so_model.copy(sale_ids[0], {},
                                 context={'order_type': 'sale_order'})
        so_model.action_button_confirm([order_id, ])


class Seller(OdooLocust):
    # host = "127.0.0.1"
    # database = "PABI2-1"
    # host = "appdev02.nstda.or.th"
    # port = 9001
    host = "pabi2o-test.intra.nstda.or.th"
    port = 80
    database = "PABI2_ptest"
    login = "admin"
    password = "admin"
    protocol = "jsonrpc"
    min_wait = 100
    max_wait = 1000
    weight = 3
    task_set = SellerTaskSet
