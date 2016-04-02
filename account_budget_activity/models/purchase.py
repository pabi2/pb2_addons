# -*- coding: utf-8 -*-
from openerp import api, fields, models


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


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

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
    requisition_line_id = fields.Many2one(
        'purchase.requisition.line',
        string='Purchase Requisition Line',
    )
    invoiced_qty = fields.Float(
        string='Invoiced Quantity',
        digits=(12, 6),
        compute='_compute_invoiced_qty',
        store=True,
        help="This field calculate invoiced quantity at line level. "
        "Will be used to calculate committed budget",
    )

    @api.multi
    @api.depends('invoice_lines.invoice_id.state')
    def _compute_invoiced_qty(self):
        Uom = self.env['product.uom']
        for po_line in self:
            invoiced_qty = 0.0
            for invoice_line in po_line.invoice_lines:
                if invoice_line.invoice_id.state not in ['draft', 'cancel']:
                    # Invoiced Qty in PO Line's UOM
                    invoiced_qty += Uom._compute_qty(invoice_line.uos_id.id,
                                                     invoice_line.quantity,
                                                     po_line.product_uom.id)
            po_line.invoiced_qty = min(po_line.product_qty, invoiced_qty)

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
            date_planned = date_planned or fields.Date.today()
            res['value'].update({'date_planned': date_planned})
        return res
