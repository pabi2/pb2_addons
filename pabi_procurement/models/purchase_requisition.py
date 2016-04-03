# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
import time


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    purchase_type_id = fields.Many2one(
        'purchase.type',
        string='Type',
    )
    objective = fields.Text(
        string='Objective',
    )
    total_budget_value = fields.Float(
        string='Total Budget Value',
        default=0.0,
    )
    prototype = fields.Boolean(
        string='Prototype',
        default=False,
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Method',
        track_visibility='onchange',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )
    currency_rate = fields.Float(
        string='Rate',
    )
    committee_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        string='Committee',
    )
    attachment_ids = fields.One2many(
        'purchase.requisition.attachment',
        'requisition_id',
        string='Attach Files',
    )
    amount_untaxed = fields.Float(
        string='Untaxed Amount',
        readonly=True,
        default=0.0,
    )
    amount_tax = fields.Float(
        string='Taxes',
        readonly=True,
        default=0.0,
    )
    amount_total = fields.Float(
        string='Total',
        readonly=True,
        default=0.0,
    )
    approval_document_no = fields.Char(
        string='No.',
    )
    approval_document_date = fields.Date(
        string='Date of Approval',
        help="Date of the order has been approved ",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    approval_document_header = fields.Text(
        string='Header',
    )
    approval_document_footer = fields.Text(
        string='Footer',
    )

    @api.model
    def create(self, vals):
        AccTax = self.env['account.tax']
        total_untaxed = 0.0
        tax_amount = 0.0
        if 'line_ids' in vals:
            if len(vals['line_ids']) > 0:
                for line_rec in vals['line_ids']:
                    field = line_rec[2]
                    for rec_taxes in field['taxes_id']:
                        for rec_tax in rec_taxes[2]:
                            domain = [('id', '=', rec_tax)]
                            found_tax = AccTax.search(domain)
                            if found_tax.type == 'percent':
                                tax_amount += field['product_qty'] * (
                                    field['price_unit'] * found_tax.amount
                                )
                            elif found_tax.type == 'fixed':
                                tax_amount += field['product_qty'] * (
                                    field['price_unit'] + found_tax.amount
                                )
                    untaxed = field['product_qty'] * field['price_unit']
                    total_untaxed += untaxed
        vals.update({
            'amount_untaxed': total_untaxed,
            'amount_tax': tax_amount,
            'amount_total': total_untaxed + tax_amount,
        })
        create_rec = super(PurchaseRequisition, self).create(vals)
        return create_rec

    @api.multi
    def write(self, vals):
        PRLine = self.env['purchase.requisition.line']
        sum_total = 0.0
        total_untaxed = 0.0
        tax_amount = 0.0
        domain = [('requisition_id', '=', self.id)]
        found_recs = PRLine.search(domain)
        for rec in found_recs:
            for rec_tax in rec.taxes_id:
                if rec_tax.type == 'percent':
                    tax_amount += rec.product_qty * (
                        rec.price_unit * rec_tax.amount
                    )
                elif rec_tax.type == 'fixed':
                    tax_amount += rec.product_qty * (
                        rec.price_unit + rec_tax.amount
                    )
            total_untaxed += rec.product_qty * rec.price_unit
            sum_total += rec.price_subtotal
        vals.update({
            'amount_untaxed': total_untaxed,
            'amount_tax': tax_amount,
            'amount_total': sum_total,
        })
        res = super(PurchaseRequisition, self).write(vals)
        return res

    @api.model
    def open_price_comparison(self, ids):
        window_obj = self.env["ir.actions.act_window"]
        res = window_obj.for_xml_id('purchase', 'purchase_line_form_action2')
        pur_line_ids = []
        po_recs = self.browse(ids)
        for po_rec in po_recs:
            pur_line_ids = po_rec.purchase_ids._ids
        res['context'] = self._context
        res['domain'] = [('order_id', 'in', pur_line_ids)]
        return res

    @api.multi
    def by_pass_approve(self):
        po_obj = self.env["purchase.order"]
        po_obj.action_button_convert_to_order()
        return True


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    price_unit = fields.Float(
        string='Unit Price',
    )
    fixed_asset = fields.Boolean('Fixed Asset')
    price_subtotal = fields.Float(
        string='Sub Total',
        compute="_compute_price_subtotal",
        store=True,
        digits_compute=dp.get_precision('Account')
    )
    taxes_id = fields.Many2many(
        'account.tax',
        'purchase_requisition_taxe',
        'requisition_line_id',
        'tax_id',
        string='Taxes'
    )
    order_line_id = fields.Many2one(
        'purchase_order_line',
        string='Purchase Order Line'
    )
    product_name = fields.Char(string='Description')

    @api.multi
    def onchange_product_id(self, product_id, product_uom_id,
                            parent_analytic_account, analytic_account,
                            parent_date, date):
        res = super(PurchaseRequisitionLine, self).\
            onchange_product_id(product_id, product_uom_id,
                                parent_analytic_account, analytic_account,
                                parent_date, date)
        if 'value' in res:
            if 'product_qty' in res['value']:
                del res['value']['product_qty']
        return res

    @api.multi
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_price_subtotal(self):
        tax_amount = 0.0
        for line in self:
            amount_untaxed = line.product_qty * line.price_unit
            for line_tax in line.taxes_id:
                if line_tax.type == 'percent':
                    tax_amount += line.product_qty * (
                        line.price_unit * line_tax.amount
                    )
                elif line_tax.type == 'fixed':
                    tax_amount += line.product_qty * (
                        line.price_unit + line_tax.amount
                    )
            cur = line.requisition_id.currency_id
            line.price_subtotal = cur.round(amount_untaxed + tax_amount)
