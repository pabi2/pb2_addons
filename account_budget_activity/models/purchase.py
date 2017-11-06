# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
from .account_activity import ActivityCommon


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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


class PurchaseOrderLine(ActivityCommon, models.Model):
    _inherit = 'purchase.order.line'

    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        string='Purchase Requisition Line',
    )
    # temp_invoiced_qty = fields.Float(
    #     string='Temporary Invoiced Quantity',
    #     digits=(12, 6),
    #     compute='_compute_temp_invoiced_qty',
    #     store=True,
    #     copy=False,
    #     default=0.0,
    #     help="This field is used to keep the previous invoice qty, "
    #     "for calculate release commitment amount",
    # )

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

    @api.multi
    def _prepare_analytic_line(self, reverse=False, currency=False):
        self.ensure_one()
        # general_account_id = self._get_account_id_from_po_line()
        general_journal = self.env['account.journal'].search(
            [('type', '=', 'purchase'),
             ('company_id', '=', self.company_id.id)], limit=1)
        if not general_journal:
            raise Warning(_('Define an accounting journal for purchase'))
        if not general_journal.is_budget_commit:
            return False
        if not general_journal.po_commitment_analytic_journal_id or \
                not general_journal.po_commitment_account_id:
            raise ValidationError(
                _("No analytic journal for PO commitments defined on the "
                  "accounting journal '%s'") % general_journal.name)
        analytic_journal = general_journal.po_commitment_analytic_journal_id

        # Pre check, is eligible line
        Budget = self.env['account.budget']
        if not Budget.budget_eligible_line(analytic_journal, self):
            return False

        # Use PO Commitment Account
        general_account_id = general_journal.po_commitment_account_id.id

        line_qty = 0.0
        if 'diff_qty' in self._context:
            line_qty = self._context.get('diff_qty')
        else:
            line_qty = self.product_qty - self.open_invoiced_qty
        if not line_qty:
            return False
        sign = reverse and -1 or 1
        company_currency = self.env.user.company_id.currency_id
        currency = currency or company_currency
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'account_id': self.account_analytic_id.id,
            'unit_amount': line_qty,
            'product_uom_id': self.product_uom.id,
            'amount': currency.compute(sign * self._price_subtotal(line_qty),
                                       company_currency),
            'general_account_id': general_account_id,
            'journal_id': analytic_journal.id,
            'ref': self.order_id.name,
            'user_id': self._uid,
            # PO
            'purchase_id': self.order_id.id,
        }

    @api.one
    def _create_analytic_line(self, reverse=False):
        if 'order_type' in self.order_id and \
                self.order_id.order_type == 'quotation':  # Not for quotation.
            return
        vals = self._prepare_analytic_line(
            reverse=reverse, currency=self.order_id.currency_id)
        if vals:
            self.env['account.analytic.line'].sudo().create(vals)

    # When confirm PO Line, create full analytic lines
    @api.multi
    def action_confirm(self):
        res = super(PurchaseOrderLine, self).action_confirm()
        self._create_analytic_line(reverse=True)
        return res

    # When cancel or set done
    @api.multi
    def write(self, vals):
        # Create negative amount for the remain product_qty - open_invoiced_qty
        if vals.get('state') in ('done', 'cancel'):
            self.filtered(lambda l: l.state not in ('done',
                                                    'draft', 'cancel')).\
                _create_analytic_line(reverse=False)
        return super(PurchaseOrderLine, self).write(vals)

    # # When partial open_invoiced_qty
    # @api.multi
    # @api.depends('open_invoiced_qty')
    # def _compute_temp_invoiced_qty(self):
    #     # As inoviced_qty increased, release the commitment
    #     for rec in self:
    #         # On compute filed of temp_purchased_qty, ORM is not working
    #         self._cr.execute("""
    #             select temp_invoiced_qty
    #             from purchase_order_line where id = %s
    #         """, (rec.id,))
    #         result = self._cr.fetchone()
    #         temp_invoiced_qty = result and result[0] or 0.0
    #         diff_qty = (rec.open_invoiced_qty - temp_invoiced_qty)
    #         if rec.state not in ('done', 'draft', 'cancel'):
    #             rec.with_context(diff_qty=diff_qty).\
    #                 _create_analytic_line(reverse=False)
    #         rec.temp_invoiced_qty = rec.open_invoiced_qty

    # ======================================================
