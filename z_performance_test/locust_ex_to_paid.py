from locust import task, TaskSet
from OdooLocust import OdooLocust


class EXTaskSet(TaskSet):
    @task(20)
    def ex_to_paid(self):
        Expense = self.client.get_model('hr.expense.expense')
        expense_ids = Expense.search([('number', '=', 'EX18000001')])
        expense_id = Expense.copy(expense_ids[0], {})
        Expense.signal_workflow([expense_id], 'confirm')
        ctx = {'active_model': 'hr.expense.expense', 'active_id': expense_id}
        Expense.action_accept_to_paid([expense_id], context=ctx)


class EX(OdooLocust):
    host = "127.0.0.1"
    database = "PABI2_int3"
    port = 8069
    # host = "pabi2o-test.intra.nstda.or.th"
    # port = 80
    # database = "PABI2_ptest"
    login = "admin"
    password = "admin"
    protocol = "jsonrpc"
    min_wait = 100
    max_wait = 1000
    weight = 3
    task_set = EXTaskSet
