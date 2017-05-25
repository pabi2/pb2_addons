# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _purchase_budget_check(self):
        Budget = self.env['account.budget']
        for purchase in self:
            doc_date = purchase.date_order
            doc_lines = Budget.convert_lines_to_doc_lines(purchase.order_line)
            res = Budget.post_commit_budget_check(doc_date, doc_lines)
            if not res['budget_ok']:
                raise ValidationError(res['message'])
        return True

    @api.multi
    def wkf_confirm_order(self):
        res = super(PurchaseOrder, self).wkf_confirm_order()
        self._purchase_budget_check()
        return res
