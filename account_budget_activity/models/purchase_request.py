# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .account_activity import ActivityCommon
from .budget_commit import CommitCommon
from .budget_commit import CommitLineCommon


class PurchaseRequest(CommitCommon, models.Model):
    _inherit = 'purchase.request'

    # Extension to budget_transition.py
    budget_commit_ids = fields.One2many(inverse_name='purchase_request_id')
    budget_transition_ids = fields.One2many(inverse_name='purchase_request_id')

    @api.multi
    def button_to_approve(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_to_approve()

    @api.multi
    def button_approved(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_approved()

    @api.multi
    def write(self, vals):
        # Create analytic when approved by PRWeb and be come To Accept in PR
        if vals.get('state') in ['to_approve']:
            self.line_ids.filtered(lambda l:
                                   l.request_state not in ('to_approve',)).\
                _create_analytic_line(reverse=True)
        # Clear all budget, if any.
        if vals.get('state') in ('draft', 'done', 'rejected'):
            self.release_all_committed_budget()
        return super(PurchaseRequest, self).write(vals)


class PurchaseRequestLine(CommitLineCommon, ActivityCommon, models.Model):
    _inherit = 'purchase.request.line'

    budget_commit_ids = fields.One2many(
        inverse_name='purchase_request_line_id')
    budget_transition_ids = fields.One2many(
        inverse_name='purchase_request_line_id')

    # purchased_qty = fields.Float(
    #     string='Purchased Quantity',
    #     digits=(12, 6),
    #     compute='_compute_purchased_qty',
    #     store=True,
    #     help="This field calculate purchased quantity at line level. "
    #     "Will be used to calculate committed budget",
    # )
    price_unit = fields.Float(
        string='Unit Price',
    )
    # We neeed the missing link to purchase_lines,
    # this is mock with view purchase_request_purchase_order_line_rel
    purchase_lines = fields.Many2many(
        'purchase.order.line',
        'purchase_request_purchase_order_line_rel',
        'purchase_request_line_id',
        'purchase_order_line_id',
        string='Purchase Order Lines',
        compute='_compute_purchase_lines',
        store=True,
        help="purchase_request_purchase_order_line_rel is a View."
    )
    # budget_commit_ids = fields.One2many(
    #     'account.analytic.line',
    #     'purchase_request_line_id',
    #     string='Budget Commitment',
    #     readonly=True,
    # )
    # budget_commit_bal = fields.Float(
    #     string='Budget Balance',
    #     compute='_compute_budget_commit_bal',
    # )
    # budget_transition_ids = fields.One2many(
    #     'budget.transition',
    #     'purchase_request_line_id',
    #     string='Budget Transition',
    #     domain=[('source_model', '=', 'purchase.request.line'),
    #             '|', ('active', '=', True), ('active', '=', False)],
    #     readonly=True,
    # )

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.request_id.name or '-',
                              line.name or '-')))
        return result

    # @api.model   # kittiu: TOBE DELETED
    # def _get_purchase_lines_view_sql(self):
    #     return """
    #     select purchase_request_line_id, pol.id as purchase_order_line_id
    #     from purchase_request_purchase_requisition_line_rel prq
    #     join purchase_order_line pol
    #     on pol.requisition_line_id = prq.purchase_requisition_line_id
    #     """

    @api.multi
    @api.depends('requisition_lines.purchase_line_ids.pur_line_id')
    def _compute_purchase_lines(self):
        for rec in self:
            rec.purchase_lines = \
                rec.requisition_lines.mapped('purchase_line_ids.pur_line_id')

    # @api.multi
    # def _compute_budget_commit_bal(self):
    #     for rec in self:
    #       rec.budget_commit_bal = sum(rec.budget_commit_ids.mapped('amount'))
    #
    # @api.multi
    # def release_committed_budget(self):
    #     _field = 'purchase_request_line_id'
    #     Analytic = self.env['account.analytic.line']
    #     for rec in self:
    #         aline = Analytic.search([(_field, '=', rec.id)],
    #                                 order='create_date desc', limit=1)
    #         if aline and rec.budget_commit_bal:
    #             aline.copy({'amount': -rec.budget_commit_bal})

    # @api.multi
    # @api.depends('requisition_lines.purchase_line_ids.order_id.state')
    # def _compute_purchased_qty(self):
    #     Uom = self.env['product.uom']
    #     for request_line in self:
    #         purchased_qty = 0.0
    #         for reqisition_line in request_line.requisition_lines:
    #             for purchase_line in reqisition_line.purchase_line_ids:
    #                 if purchase_line.order_id.state in ['approved']:
    #                     # Purchased Qty in PO Line's UOM
    #                     purchased_qty += \
    #                         Uom._compute_qty(purchase_line.product_uom.id,
    #                                          purchase_line.product_qty,
    #                                          request_line.product_uom_id.id)
    #         request_line.purchased_qty = min(request_line.product_qty,
    #                                          purchased_qty)

    # ================= PR Commitment =====================
    # DO NOT DELETE, Pending decision on what to use.
    #     @api.model
    #     def _get_account_id_from_pr_line(self):
    #         account = self.activity_group_id.account_id
    #         # If not exist, use the default expense account
    #         if not account:
    #             prop = self.env['ir.property'].search(
    #                 [('name', '=', 'property_account_expense_categ')])
    #             account = prop.get_by_record(prop)
    #         return account and account.id or False

    @api.model
    def _price_subtotal(self, line_qty):
        return self.price_subtotal
        # return self.price_unit * line_qty

    # @api.multi
    # def _prepare_analytic_line(self, reverse=False, currency=False):
    #     self.ensure_one()
    #     # general_account_id = self._get_account_id_from_pr_line()
    #     general_journal = self.env['account.journal'].search(
    #         [('type', '=', 'purchase'),
    #          ('company_id', '=', self.company_id.id)], limit=1)
    #     if not general_journal:
    #         raise Warning(_('Define an accounting journal for purchase'))
    #     if not general_journal.is_budget_commit:
    #         return False
    #     if not general_journal.pr_commitment_analytic_journal_id or \
    #             not general_journal.pr_commitment_account_id:
    #         raise ValidationError(
    #             _("No analytic journal for PR commitment defined on the "
    #               "accounting journal '%s'") % general_journal.name)
    #     analytic_journal = general_journal.pr_commitment_analytic_journal_id
    #
    #     # Pre check, is eligible line
    #     Budget = self.env['account.budget']
    #     if not Budget.budget_eligible_line(analytic_journal, self):
    #         return False
    #
    #     # Use PR Commitment Account
    #     general_account_id = general_journal.pr_commitment_account_id.id
    #
    #     line_qty = False
    #     line_amount = False
    #     if 'diff_qty' in self._context:
    #         line_qty = self._context.get('diff_qty')
    #     elif 'diff_amount' in self._context:
    #         line_amount = self._context.get('diff_amount')
    #     else:
    #         line_qty = self.product_qty
    #     if not line_qty and not line_amount:
    #         return False
    #     price_subtotal = line_amount or self._price_subtotal(line_qty)
    #
    #     sign = reverse and -1 or 1
    #     company_currency = self.env.user.company_id.currency_id
    #     currency = currency or company_currency
    #     return {
    #         'name': self.name,
    #         'product_id': False,
    #         'account_id': self.analytic_account_id.id,
    #         'unit_amount': line_qty,
    #         'product_uom_id': False,
    #         'amount': currency.compute(sign * price_subtotal,
    #                                    company_currency),
    #         'general_account_id': general_account_id,
    #         'journal_id': analytic_journal.id,
    #         'ref': self.request_id.name,
    #         'user_id': self._uid,
    #         # PR
    #         'purchase_request_line_id': self.id,
    #         # Fiscal
    #         'fiscalyear_id': self.fiscalyear_id.id,
    #     }
    #
    # @api.multi
    # def _create_analytic_line(self, reverse=False):
    #     for rec in self:
    #         vals = rec._prepare_analytic_line(
    #             reverse=reverse, currency=rec.request_id.currency_id)
    #         if vals:
    #             self.env['account.analytic.line'].sudo().create(vals)
