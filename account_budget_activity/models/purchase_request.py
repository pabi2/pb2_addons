# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import except_orm, Warning


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

#     @api.multi
#     def _invoice_budget_check(self):
#         AccountBudget = self.env['account.budget']
#         for invoice in self:
#             if invoice.type != 'in_invoice':
#                 continue
#             # Get fiscal year and budget level for this group
#             fiscal_id, budgeting_level = AccountBudget.\
#                 get_fiscal_and_budgeting_level(invoice.date_invoice)
#             # Find amount in this invoice to check against budget
#             self._cr.execute("""
#                 select %(budgeting_level)s,
#                 coalesce(sum(price_subtotal), 0.0) amount
#                 from account_invoice_line where invoice_id = %(invoice_id)s
#                 group by %(budgeting_level)s
#             """ % {'budgeting_level': budgeting_level,
#                    'invoice_id': invoice.id}
#             )
#             # Check budget at this budgeting level
#             for r in self._cr.dictfetchall():
#                 res = AccountBudget.check_budget(r['amount'],
#                                                  r[budgeting_level],
#                                                  fiscal_id,
#                                                  budgeting_level)
#                 if not res['budget_ok']:
#                     raise Warning(res['message'])
#         return True

#     @api.multi
#     def action_date_assign(self):
#         self._invoice_budget_check()
#         return super(AccountInvoice, self).action_date_assign()

    @api.multi
    def button_to_approve(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_to_approve()


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=False,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=False,
    )

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        self.product_id = False
        self.activity_group_id = self.activity_id.activity_group_id

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        super(PurchaseRequestLine, self).onchange_product_id()
        self.activity_group_id = False
        self.activity_id = False
