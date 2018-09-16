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

    # @api.multi
    # def _compute_budget_commit_bal(self):
    #     for rec in self:
    #       rec.budget_commit_bal = sum(rec.budget_commit_ids.mapped('amount'))
    #
    # @api.multi
    # def release_committed_budget(self):
    #     _field = 'expense_line_id'
    #     Analytic = self.env['account.analytic.line']
    #     for rec in self:
    #         aline = Analytic.search([(_field, '=', rec.id)],
    #                                 order='create_date desc', limit=1)
    #         if aline and rec.budget_commit_bal:
    #             aline.copy({'amount': -rec.budget_commit_bal})

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

    # @api.model
    # def _prepare_analytic_line(self, reverse=False, currency=False):
    #     self.ensure_one()
    #     # general_account_id = self._get_account_id_from_po_line()
    #     general_journal = self.env['account.journal'].search(
    #         [('type', '=', 'purchase')], limit=1)   # <--- TYPE
    #     if not general_journal:
    #         raise Warning(_('Define an accounting journal for purchase'))
    #     if not general_journal.is_budget_commit:
    #         return False
    #     if not general_journal.exp_commitment_analytic_journal_id or \
    #             not general_journal.exp_commitment_account_id:  # <---
    #         raise ValidationError(
    #         _("No analytic journal for expense commitments defined on the "
    #               "accounting journal '%s'") % general_journal.name)
    #     analytic_journal = general_journal.exp_commitment_analytic_journal_id
    #
    #     # Pre check, is eligible line
    #     Budget = self.env['account.budget']
    #     if not Budget.budget_eligible_line(analytic_journal, self):
    #         return False
    #
    #     # Use EX Commitment Account
    # general_account_id = general_journal.exp_commitment_account_id.id #  < --
    #
    #     line_qty = False
    #     line_amount = False
    #     if 'diff_qty' in self._context:
    #         line_qty = self._context.get('diff_qty')
    #     elif 'diff_amount' in self._context:
    #         line_amount = self._context.get('diff_amount')
    #     else:
    #         line_qty = self.unit_quantity   # <--- Field
    #     if not line_qty and not line_amount:
    #         return False
    #     price_subtotal = line_amount or self._price_subtotal(line_qty)
    #
    #     sign = reverse and -1 or 1
    #     company_currency = self.env.user.company_id.currency_id
    #     currency = currency or company_currency
    #     return {
    #         'name': self.name,
    #         'product_id': self.product_id.id,     # <--- Project
    #         'account_id': self.analytic_account.id,    # <-- anatlyic account
    #         'unit_amount': line_qty,
    #         'product_uom_id': self.uom_id.id,
    #         'amount': currency.compute(sign * price_subtotal,
    #                                    company_currency),
    #         'general_account_id': general_account_id,
    #         'journal_id': analytic_journal.id,
    #         'ref': self.expense_id.name,
    #         'user_id': self._uid,
    #         # Expense
    #         'expense_line_id': self.id,   # <-- ID to Expense Line
    #     }
    #
    # @api.multi
    # def _create_analytic_line(self, reverse=False):
    #     for rec in self:
    #         vals = rec._prepare_analytic_line(
    #             reverse=reverse, currency=rec.expense_id.currency_id)
    #         if vals:
    #             self.env['account.analytic.line'].sudo().create(vals)

    # # When partial open_invoiced_qty
    # @api.multi
    # @api.depends('open_invoiced_qty')
    # def _compute_temp_invoiced_qty(self):
    #     # As inoviced_qty increased, release the commitment
    #     for rec in self:
    #         # On compute filed of temp_purchased_qty, ORM is not working
    #         self._cr.execute("""
    #             select temp_invoiced_qty
    #             from hr_expense_line where id = %s
    #         """, (rec.id,))
    #         result = self._cr.fetchone()
    #         temp_invoiced_qty = result and result[0] or 0.0
    #         diff_qty = (rec.open_invoiced_qty - temp_invoiced_qty)
    #         if rec.expense_state not in ('cancelled',):
    #             x = 1
    #             rec.with_context(diff_qty=diff_qty).\
    #                 _create_analytic_line(reverse=False)
    #         rec.temp_invoiced_qty = rec.open_invoiced_qty

    # ======================================================
