# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _expense_budget_check(self):
        Budget = self.env['account.budget']
        for expense in self:
            # Get budget level type resources
            r = Budget.get_fiscal_and_budget_level(expense.date)
            fiscal_id = r['fiscal_id']
            # Check for all budget types
            
            if 'invest_construction' in r:
                r['invest_construction'] = 'invest_construction_id'
            
            for budget_type in dict(Budget.BUDGET_LEVEL_TYPE).keys():
                if budget_type not in r:
                    raise UserError(_('Budget level is not set!'))
                budget_level = r[budget_type]  # specify what to check
                # Find amount in this expense to check against budget
                self._cr.execute("""
                    select hel.%(budget_level)s,
                        coalesce(sum(hel.total_amount), 0.0) amount
                    from hr_expense_line hel
                    join hr_expense_expense he on he.id = hel.expense_id
                    where he.id = %(expense_id)s
                    group by hel.%(budget_level)s
                """ % {'budget_level': budget_level,
                       'expense_id': expense.id}
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
