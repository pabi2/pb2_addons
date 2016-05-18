# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # -- Budget Check for Activity Group Level --
    # DO NOT DELETE
#     @api.multi
#     def _invoice_budget_check(self):
#         """ Overwrite to comply with Unit Base / Project Base """
#         AccountBudget = self.env['account.budget']
#         for invoice in self:
#             if invoice.type != 'in_invoice':
#                 continue
#             date = invoice.date_invoice
#             r = AccountBudget.get_fiscal_and_budget_level(date)
#             fiscal_id = r['fiscal_id']
#             query = """
#                 select %(field)s,
#                     coalesce(sum(price_subtotal), 0.0) amount
#                 from account_invoice_line
#                 where invoice_id = %(invoice_id)s
#                     and %(pu_field)s is not null
#                 group by %(field)s
#             """
#             # Check budget for both project and unit base
#             for budget_type in ['check_budget_project_base',
#                                 'check_budget_unit_base']:
#                 if budget_type not in r:
#                     raise UserError(_('Budget level is not set!'))
#                 budget_level = r[budget_type]
#                 pu_field = (budget_type == 'check_budget_project_base' and
#                             'project_id' or 'costcenter_id')
#                 field = budget_level
#                 if budget_level in ('activity_group_id', 'activity_id'):
#                     field = pu_field + ', ' + budget_level
#                 self._cr.execute(
#                     query % {'field': field,
#                              'invoice_id': invoice.id,
#                              'pu_field': pu_field}
#                 )
#                 # Check budget at this budgeting level
#                 for rec in self._cr.dictfetchall():
#                     res = AccountBudget.check_budget(fiscal_id,
#                                                      budget_type,
#                                                      budget_level,
#                                                      rec[budget_level],
#                                                      rec['amount'],
#                                                      pu_id=rec.get(pu_field))
#                     if not res['budget_ok']:
#                         raise UserError(res['message'])
#         return True

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
