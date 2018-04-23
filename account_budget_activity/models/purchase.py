# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .account_activity import ActivityCommon
from .budget_commit import CommitCommon
from .budget_commit import CommitLineCommon


class PurchaseOrder(CommitCommon, models.Model):
    _inherit = 'purchase.order'

    # Extension to budget_transition.py
    budget_commit_ids = fields.One2many(inverse_name='purchase_id')
    budget_transition_ids = fields.One2many(inverse_name='purchase_id')

    @api.multi
    def wkf_confirm_order(self):
        for purchase in self:
            for line in purchase.order_line:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseOrder, self).wkf_confirm_order()

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self).\
            _prepare_inv_line(account_id, order_line)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: order_line[d].id})
        return res

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self).\
            _prepare_order_line_move(order, order_line,
                                     picking_id, group_id)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            for r in res:
                r.update({d: order_line[d].id})
        return res

    # When draft, cancel or set done, clear all budget
    @api.multi
    def write(self, vals):
        if vals.get('state') in ('draft', 'done', 'cancel'):
            self.release_all_committed_budget()
        return super(PurchaseOrder, self).write(vals)


class PurchaseOrderLine(CommitLineCommon, ActivityCommon, models.Model):
    _inherit = 'purchase.order.line'

    budget_commit_ids = fields.One2many(inverse_name='purchase_line_id')
    budget_transition_ids = fields.One2many(inverse_name='purchase_line_id')

    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        string='Purchase Requisition Line',
    )

    # @api.multi
    # def _compute_budget_commit_bal(self):
    #     for rec in self:
    #       rec.budget_commit_bal = sum(rec.budget_commit_ids.mapped('amount'))
    #
    # @api.multi
    # def release_committed_budget(self):
    #     _field = 'purchase_line_id'
    #     Analytic = self.env['account.analytic.line']
    #     for rec in self:
    #         aline = Analytic.search([(_field, '=', rec.id)],
    #                                 order='create_date desc', limit=1)
    #         if aline and rec.budget_commit_bal:
    #             aline.copy({'amount': -rec.budget_commit_bal})

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            result.append(
                (line.id,
                 "%s / %s" % (line.order_id.name or '-',
                              line.name or '-')))
        return result

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name,
            price_unit=price_unit, state=state)
        if not res['value'].get('date_planned', False):
            date_planned = date_planned or fields.Date.context_today(self)
            res['value'].update({'date_planned': date_planned})
        return res

    # ================= Purchase Commitment =====================
    # DO NOT DELETE, Pending decision on what to use.
    #     @api.model
    #     def _get_account_id_from_po_line(self):
    #         # For PABI, account is always from activity group
    #         account = self.activity_group_id.account_id
    #         # If not exist, use the default expense account
    #         if not account:
    #             prop = self.env['ir.property'].search(
    #                 [('name', '=', 'property_account_expense_categ')])
    #             account = prop.get_by_record(prop)
    #         return account and account.id or False

    @api.model
    def _price_subtotal(self, line_qty):
        line_price = self._calc_line_base_price(self)
        taxes = self.taxes_id.compute_all(line_price, line_qty,
                                          self.product_id,
                                          self.order_id.partner_id)
        cur = self.order_id.pricelist_id.currency_id
        return cur.round(taxes['total'])

    # @api.multi
    # def _prepare_analytic_line(self, reverse=False, currency=False):
    #     self.ensure_one()
    #     # general_account_id = self._get_account_id_from_po_line()
    #     general_journal = self.env['account.journal'].search(
    #         [('type', '=', 'purchase'),
    #          ('company_id', '=', self.company_id.id)], limit=1)
    #     if not general_journal:
    #         raise Warning(_('Define an accounting journal for purchase'))
    #     if not general_journal.is_budget_commit:
    #         return False
    #     if not general_journal.po_commitment_analytic_journal_id or \
    #             not general_journal.po_commitment_account_id:
    #         raise ValidationError(
    #             _("No analytic journal for PO commitments defined on the "
    #               "accounting journal '%s'") % general_journal.name)
    #     analytic_journal = general_journal.po_commitment_analytic_journal_id
    #
    #     # Pre check, is eligible line
    #     Budget = self.env['account.budget']
    #     if not Budget.budget_eligible_line(analytic_journal, self):
    #         return False
    #
    #     # Use PO Commitment Account
    #     general_account_id = general_journal.po_commitment_account_id.id
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
    #         'product_id': self.product_id.id,
    #         'account_id': self.account_analytic_id.id,
    #         'unit_amount': line_qty,
    #         'product_uom_id': self.product_uom.id,
    #         'amount': currency.compute(sign * price_subtotal,
    #                                    company_currency),
    #         'general_account_id': general_account_id,
    #         'journal_id': analytic_journal.id,
    #         'ref': self.order_id.name,
    #         'user_id': self._uid,
    #         # PO
    #         'purchase_line_id': self.id,
    #         # Fiscal
    #         'fiscalyear_id': self.fiscalyear_id.id,
    #     }
    #
    # @api.multi
    # def _create_analytic_line(self, reverse=False):
    #     for rec in self:
    #         if 'order_type' in rec.order_id and \
    #                 rec.order_id.order_type == 'quotation':  # Not quotation.
    #             continue
    #         vals = rec._prepare_analytic_line(
    #             reverse=reverse, currency=rec.order_id.currency_id)
    #         if vals:
    #             self.env['account.analytic.line'].sudo().create(vals)

    # When confirm PO Line, create full analytic lines
    @api.multi
    def action_confirm(self):
        res = super(PurchaseOrderLine, self).action_confirm()
        self._create_analytic_line(reverse=True)
        return res
