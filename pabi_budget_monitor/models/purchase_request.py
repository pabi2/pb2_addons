# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def _pr_budget_check(self):
        Budget = self.env['account.budget']
        for pr in self:
            # issue : https://mobileapp.nstda.or.th/redmine/issues/4099
            # Change date pr to date today
            doc_date = fields.Date.context_today(self)
            # doc_date = pr.date_approve
            doc_lines = Budget.convert_lines_to_doc_lines(pr.line_ids)
            res = Budget.post_commit_budget_check(doc_date, doc_lines)
            if not res['budget_ok']:
                raise ValidationError(res['message'])
        return True

    @api.multi
    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        # Create analytic when approved by PRWeb and be come To Accept in PR
        if vals.get('state') in ['to_approve']:
            self._pr_budget_check()
        return res

    budget_over_return = fields.Boolean(
        string='Budget Over Return',
        compute='_compute_budget_over_return',
        search='_search_budget_over_return',
        help="Show POs that return budget amount more than its commit",
    )

    @api.model
    def _get_budget_over_return_sql(self):
        return """
            select a.purchase_request_id, a.amount from
            (select purchase_request_id, sum(amount) amount
            from account_analytic_line
             where purchase_request_id is not null
            group by purchase_request_id) a
            where a.amount > 0
        """

    @api.multi
    def _compute_budget_over_return(self):
        if self.ids:
            sql = self._get_budget_over_return_sql()
            self._cr.execute(
                sql + " and purchase_id in %s", (tuple(self.ids),))
        request_ids = [row[0] for row in self._cr.fetchall()]
        for pr in self:
            if pr.id in request_ids:
                pr.budget_over_return = True
            else:
                pr.budget_over_return = False
        return True

    @api.model
    def _search_budget_over_return(self, operator, value):
        budget_over_return_pr_ids = []
        if operator == '=' and value:
            self._cr.execute(self._get_budget_over_return_sql())
            budget_over_return_pr_ids = [row[0] for row in self._cr.fetchall()]
        return [('id', 'in', budget_over_return_pr_ids)]
