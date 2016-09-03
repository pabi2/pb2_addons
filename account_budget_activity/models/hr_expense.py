# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError
from .account_activity import ActivityCommon


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _expense_budget_check(self):
        AccountBudget = self.env['account.budget']
        for expense in self:
            # Get budget level type resources
            r = AccountBudget.get_fiscal_and_budget_level(expense.date)
            fiscal_id = r['fiscal_id']
            budget_type = 'check_budget'
            if budget_type not in r:
                raise UserError(_('Budget level is not set!'))
            budget_level = r[budget_type]  # specify what to check
            # Find amount in this expense to check against budget
            self._cr.execute("""
                select %(budget_level)s,
                    coalesce(sum(hel.total_amount / cr.rate), 0.0) amount
                from hr_expense_line hel
                join hr_expense_expense he on he.id = hel.expense_id
                -- to base currency
                JOIN res_currency_rate cr ON (cr.currency_id = he.currency_id)
                    AND
                    cr.id IN (SELECT id
                      FROM res_currency_rate cr2
                      WHERE (cr2.currency_id = he.currency_id)
                          AND ((he.date IS NOT NULL
                                  AND cr2.name <= he.date)
                        OR (he.date IS NULL AND cr2.name <= NOW()))
                      ORDER BY name DESC LIMIT 1)
                --
                where he.id = %(expense_id)s
                group by %(budget_level)s
            """ % {'budget_level': budget_level,
                   'expense_id': expense.id}
            )
            context = self._context.copy()
            context.update(call_from='hr_expense_expense')
            # Check budget at this budgeting level
            for r in self._cr.dictfetchall():
                res = AccountBudget.\
                    with_context(context).\
                    check_budget(fiscal_id,
                                 budget_type,
                                 budget_level,
                                 r[budget_level],
                                 r['amount'])
                if not res['budget_ok']:
                    raise UserError(res['message'])
        return True

    @api.multi
    def expense_confirm(self):
        for expense in self:
            expense._expense_budget_check()
        return super(HRExpenseExpense, self).expense_confirm()

    @api.multi
    def expense_accept(self):
        for expense in self:
            for line in expense.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account = \
                    Analytic.create_matched_analytic(line)
        return super(HRExpenseExpense, self).expense_accept()

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
        # Commit budget as soon as Draft (approved by AP Web)
        # TODO: will only AP and not AV be in commitment?
        if vals.get('state', False) == 'draft':
            for expense in self:
                for line in expense.line_ids:
                    Analytic = self.env['account.analytic.account']
                    line.analytic_account = \
                        Analytic.create_matched_analytic(line)
            self.line_ids._create_analytic_line(reverse=True)
        # Create negative amount for the remain product_qty - open_invoiced_qty
        if vals.get('state') in ('cancelled',):
            self.filtered(lambda x: x.state not in ('cancelled',)).\
                line_ids._create_analytic_line(reverse=False)
        return super(HRExpenseExpense, self).write(vals)


class HRExpenseLine(ActivityCommon, models.Model):
    _inherit = 'hr.expense.line'

    temp_invoiced_qty = fields.Float(
        string='Temporary Invoiced Quantity',
        digits=(12, 6),
        compute='_compute_temp_invoiced_qty',
        store=True,
        copy=False,
        default=0.0,
        help="This field is used to keep the previous invoice qty, "
        "for calculate release commitment amount",
    )

    @api.model
    def _get_non_product_account_id(self):
        if 'activity_id' in self:
            if not self.activity_id.account_id:
                raise UserError(
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

    @api.model
    def _prepare_analytic_line(self, reverse=False):
        # general_account_id = self._get_account_id_from_po_line()
        general_journal = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1)
        if not general_journal:
            raise Warning(_('Define an accounting journal for purchase'))
        if not general_journal.is_budget_commit:
            return False
        if not general_journal.exp_commitment_analytic_journal_id or \
                not general_journal.exp_commitment_account_id:
            raise UserError(
                _("No analytic journal for expense commitments defined on the "
                  "accounting journal '%s'") % general_journal.name)

        # Use EXP Commitment Account
        general_account_id = general_journal.exp_commitment_account_id.id
        journal_id = general_journal.exp_commitment_analytic_journal_id.id
        line_qty = 0.0
        if 'diff_invoiced_qty' in self._context:
            line_qty = self._context.get('diff_invoiced_qty')
        else:
            line_qty = self.unit_quantity - self.open_invoiced_qty
        if not line_qty:
            return False
        sign = reverse and -1 or 1

        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'account_id': self.analytic_account.id,
            'unit_amount': line_qty,
            'product_uom_id': self.uom_id.id,
            'amount': sign * self._price_subtotal(line_qty),
            'general_account_id': general_account_id,
            'journal_id': journal_id,
            'ref': self.expense_id.name,
            'user_id': self._uid,
            'doc_ref': self.expense_id.name,
            'doc_id': '%s,%s' % ('hr.expense.expense', self.expense_id.id),
        }

    @api.one
    def _create_analytic_line(self, reverse=False):
        vals = self._prepare_analytic_line(reverse=reverse)
        if vals:
            self.env['account.analytic.line'].create(vals)

    # When partial open_invoiced_qty
    @api.multi
    @api.depends('open_invoiced_qty')
    def _compute_temp_invoiced_qty(self):
        # As inoviced_qty increased, release the commitment
        for rec in self:
            # On compute filed of temp_purchased_qty, ORM is not working
            self._cr.execute("""
                select temp_invoiced_qty
                from hr_expense_line where id = %s
            """, (rec.id,))
            result = self._cr.fetchone()
            temp_invoiced_qty = result and result[0] or 0.0
            diff_invoiced_qty = (rec.open_invoiced_qty - temp_invoiced_qty)
            if rec.expense_state not in ('cancelled',):
                rec.with_context(diff_invoiced_qty=diff_invoiced_qty).\
                    _create_analytic_line(reverse=False)
            rec.temp_invoiced_qty = rec.open_invoiced_qty

    # ======================================================
