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
        'Type',
    )
    objective = fields.Text('Objective')
    total_budget_value = fields.Float('Total Budget Value', default=0.0)
    prototype = fields.Boolean(
        string='Prototype',
        default=False,
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        'Method',
        track_visibility='onchange',
    )
    currency_id = fields.Many2one('res.currency', 'Currency')
    currency_rate = fields.Float('Rate')
    committee_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        'Committee',
    )
    attachment_ids = fields.One2many(
        'purchase.requisition.attachment',
        'requisition_id',
        'Attach Files',
    )
    amount_total = fields.Float(
        'Total',
        readonly=True,
        default=0.0,
    )
    approval_document_no = fields.Char('No.')
    approval_document_date = fields.Date(
        'Date of Approval',
        help="Date of the order has been approved ",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    approval_document_header = fields.Text('Header')
    approval_document_footer = fields.Text('Footer')

    @api.model
    def create(self, vals):
        create_rec = super(PurchaseRequisition, self).create(vals)
        sum_total = 0.0
        if 'line_ids' in vals:
            if len(vals['line_ids']) > 0:
                for line_rec in vals['line_ids']:
                    line_flds = line_rec[2]
                    sum_total += \
                        line_flds['product_qty'] * line_flds['price_unit']
            create_rec.amount_total = sum_total
        return create_rec

    @api.multi
    def write(self, vals):
        super(PurchaseRequisition, self).write(vals)
        prql_obj = self.env['purchase.requisition.line']
        sum_total = 0.0
        domain = [('requisition_id', '=', self.id)]
        found_recs = prql_obj.search(domain)
        for rec in found_recs:
            sum_total += rec.product_qty * rec.price_unit
        edited = super(PurchaseRequisition, self).\
            write({'amount_total': sum_total})
        return edited

    @api.model
    def _prepare_purchase_order_line(self, requisition, requisition_line,
                                     purchase_id, supplier):
        res = super(PurchaseRequisition, self).\
            _prepare_purchase_order_line(requisition, requisition_line,
                                         purchase_id, supplier)
        res.update({
            'requisition_line_id': requisition_line.id,
        })
        return res


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    price_unit = fields.Float(
        'Unit Price',
    )
    fixed_asset = fields.Boolean('Fixed Asset')
    price_subtotal = fields.Float(
        'Sub Total',
        compute="_amount_line",
        store=True,
        digits_compute=dp.get_precision('Account')
    )
    order_line_id = fields.Many2one(
        'purchase_order_line',
        'Purchase Order Line'
    )

    @api.depends('product_qty', 'price_unit')
    def _amount_line(self):
        self.price_subtotal = self.product_qty * self.price_unit
