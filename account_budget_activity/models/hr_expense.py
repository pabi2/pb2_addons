# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

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
            self.line_ids._create_analytic_line(reverse=True)
        # Create negative amount for the remain product_qty - invoiced_qty
        if vals.get('state') in ('cancelled',):
            self.filtered(lambda x: x.state not in ('cancelled',)).\
                line_ids._create_analytic_line(reverse=False)
        return super(HRExpenseExpense, self).write(vals)


class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        compute='_compute_activity_group',
        store=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
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

    @api.one
    @api.depends('product_id', 'activity_id')
    def _compute_activity_group(self):
        if self.product_id and self.activity_id:
            self.product_id = self.activity_id = False
            self.name = False
        if self.product_id:
            account_id = self.product_id.property_account_expense.id or \
                self.product_id.categ_id.property_account_expense_categ.id
            activity_group = self.env['account.activity.group'].\
                search([('account_id', '=', account_id)])
            self.activity_group_id = activity_group
        elif self.activity_id:
            self.activity_group_id = self.activity_id.activity_group_id
            self.name = self.activity_id.name

    @api.model
    def _get_non_product_account_id(self):
        if 'activity_group_id' in self:
            if not self.activity_group_id.account_id:
                raise UserError(
                    _('No Account Code assigned to Activity Group - %s') %
                    (self.activity_group_id.name,))
            else:
                return self.activity_group_id.account_id.id
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
            line_qty = self.unit_quantity - self.invoiced_qty
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

    # When partial invoiced_qty
    @api.multi
    @api.depends('invoiced_qty')
    def _compute_temp_invoiced_qty(self):
        # As inoviced_qty increased, release the commitment
        for rec in self:
            # On compute filed of temp_purchased_qty, ORM is not working
            self._cr.execute("""
                select temp_invoiced_qty
                from hr_expense_line where id = %s
            """, (rec.id,))
            temp_invoiced_qty = self._cr.fetchone()[0] or 0.0
            diff_invoiced_qty = rec.invoiced_qty - temp_invoiced_qty
            if rec.expense_state not in ('cancelled',):
                rec.with_context(diff_invoiced_qty=diff_invoiced_qty).\
                    _create_analytic_line(reverse=False)
            rec.temp_invoiced_qty = rec.invoiced_qty

    # ======================================================
