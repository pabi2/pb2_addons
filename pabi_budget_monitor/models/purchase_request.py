# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def _pr_budget_check(self):
        Budget = self.env['account.budget']
        for pr in self:
            doc_date = pr.date_approve
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
