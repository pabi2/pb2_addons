# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _invoice_budget_check(self):
        """ Overwrite to comply with Unit Base / Project Base """
        AccountBudget = self.env['account.budget']
        for invoice in self:
            if invoice.type != 'in_invoice':
                continue
            fiscal_id, budgeting_level, budgeting_level_unit = AccountBudget.\
                get_fiscal_and_budgeting_level(invoice.date_invoice)
            query = """
                select %(field)s,
                    coalesce(sum(price_subtotal), 0.0) amount
                from account_invoice_line
                where invoice_id = %(invoice_id)s
                    and %(project_or_unit)s is not null
                group by %(field)s
            """
            # Check budget for both project and unit base
            for project_or_unit in ['project_id', 'costcenter_id']:
                budgeting_level = (project_or_unit == 'project_id' and
                                   budgeting_level or
                                   budgeting_level_unit)
                field = budgeting_level
                # Case check to activity, combine with project or costcenter
                if budgeting_level in ('activity_group_id', 'activity_id'):
                    field = project_or_unit + ', ' + budgeting_level
                self._cr.execute(
                    query % {'field': field,
                             'invoice_id': invoice.id,
                             'project_or_unit': project_or_unit}
                )
                # Check budget at this budgeting level
                for r in self._cr.dictfetchall():
                    res = AccountBudget.check_budget(r['amount'],
                                                     r[budgeting_level],
                                                     fiscal_id,
                                                     project_or_unit,
                                                     r.get(project_or_unit))
                    if not res['budget_ok']:
                        raise UserError(res['message'])
        return True
