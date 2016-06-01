# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _invoice_budget_check(self):
        Budget = self.env['account.budget']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            # Get budget level type resources
            r = Budget.get_fiscal_and_budget_level(invoice.date_invoice)
            fiscal_id = r['fiscal_id']
            # Check for all budget types
            for budget_type in dict(Budget.BUDGET_LEVEL_TYPE).keys():
                if budget_type not in r:
                    raise UserError(_('Budget level is not set!'))
                budget_level = r[budget_type]  # specify what to check
                # Find amount in this invoice to check against budget
                self._cr.execute("""
                    select ail.%(budget_level)s,
                        coalesce(sum(ail.price_subtotal), 0.0) amount
                    from account_invoice_line ail
                    join account_invoice ai on ai.id = ail.invoice_id
                    where ai.id = %(invoice_id)s
                    group by ail.%(budget_level)s
                """ % {'budget_level': budget_level,
                       'invoice_id': invoice.id}
                )
                # Check budget at this budgeting level
                for rec in self._cr.dictfetchall():
                    if rec[budget_level]:  # If no value, do not check.
                        res = Budget.check_budget(fiscal_id,
                                                  budget_type,
                                                  budget_level,
                                                  rec[budget_level],
                                                  rec['amount'])
                        if not res['budget_ok']:
                            raise UserError(res['message'])
        return True
