# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError
from .account_activity import ActivityCommon
from .budget_commit import CommitCommon
from .budget_commit import CommitLineCommon


class HRExpenseExpense(CommitCommon, models.Model):
    _inherit = 'hr.expense.expense'

    budget_commit_ids = fields.One2many(inverse_name='expense_id')
    budget_transition_ids = fields.One2many(inverse_name='expense_id')

    @api.model
    def _prepare_inv_line(self, account_id, exp_line):
        res = super(HRExpenseExpense, self)._prepare_inv_line(account_id,
                                                              exp_line)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: exp_line[d].id})
        return res

    @api.multi
    def write(self, vals):
        if vals.get('state', False) == 'draft':
            Analytic = self.env['account.analytic.account']
            for expense in self:
                for line in expense.line_ids:
                    line.analytic_account = \
                        Analytic.create_matched_analytic(line)
                expense.line_ids._create_analytic_line(reverse=True)
        if vals.get('state') in ('cancelled',):
            self.release_all_committed_budget()
        return super(HRExpenseExpense, self).write(vals)


class HRExpenseLine(CommitLineCommon, ActivityCommon, models.Model):
    _inherit = 'hr.expense.line'

    budget_commit_ids = fields.One2many(inverse_name='expense_line_id')
    budget_transition_ids = fields.One2many(inverse_name='expense_line_id')

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.expense_id.number or '-',
                              line.name or '-')))
        return result

    @api.multi
    def _get_non_product_account_id(self):
        self.ensure_one()
        if 'activity_id' in self:
            if not self.activity_id.account_id:
                raise ValidationError(
                    _('No Account Code assigned to Activity - %s') %
                    (self.activity_id.name,))
            else:
                return self.activity_id.account_id.id
        else:
            return super(HRExpenseLine, self)._get_non_product_account_id()

    # ================= Expense Commitment =====================
    @api.model
    def _price_subtotal(self, line_qty):
        line_price = self.unit_amount
        taxes = self.tax_ids.compute_all(line_price, line_qty,
                                         self.product_id,
                                         self.expense_id.partner_id)
        cur = self.expense_id.currency_id
        return cur.round(taxes['total'])
