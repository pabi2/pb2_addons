# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import time


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    _STATES = [
        ('draft', 'Draft'),
        ('to_approve', 'To Accept'),
        ('approved', 'Accepted'),
        ('rejected', 'Cancelled')
    ]
    _ORIGINAL = {
        ('yes', 'YES'),
        ('no', 'NO'),
    }

    state = fields.Selection(
        selection=_STATES,
        string='Status',
        track_visibility='onchange',
        required=True,
        default='draft',
    )
    committee_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        'Committee',
        readonly=False,
    )
    attachment_ids = fields.One2many(
        'purchase.request.attachment',
        'request_id',
        'Attach Files',
        readonly=False,
    )
    date_approved = fields.Date(
        'Approved Date',
        help="Date when the request has been approved",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        readonly=True,
        track_visibility='onchange',
    )
    responsible_person = fields.Many2one(
        'res.users',
        'Responsible Person',
        track_visibility='onchange',
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
    )
    currency_rate = fields.Float('Rate')
    objective = fields.Text('Objective')
    purchase_method_id = fields.Many2one(
        'purchase.method',
        'Method',
    )
    prototype = fields.Boolean(
        'Prototype',
        default=False,
    )
    total_budget_value = fields.Float('Total Budget Value', default=0.0)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Warehouse',
    )
    purchase_type_id = fields.Many2one(
        'purchase.type',
        'Type',
    )
    delivery_address = fields.Text('Delivery Address')
    amount_total = fields.Float(
        'Total',
        readonly=True,
        default=0.0
    )

    @api.model
    def create(self, vals):
        create_rec = super(PurchaseRequest, self).create(vals)
        sum_total = 0.0
        if 'line_ids' in vals:
            if len(vals['line_ids']) > 0:
                for line_rec in vals['line_ids']:
                    field = line_rec[2]
                    sum_total += field['product_qty'] * field['product_price']
            create_rec.amount_total = sum_total
        return create_rec

    @api.multi
    def write(self, vals):
        super(PurchaseRequest, self).write(vals)
        prql_obj = self.env['purchase.request.line']
        sum_total = 0.0
        domain = [('request_id', '=', self.id)]
        found_recs = prql_obj.search(domain)
        for rec in found_recs:
            sum_total += rec.product_qty * rec.product_price
        edited = super(PurchaseRequest, self).\
            write({'amount_total': sum_total})
        return edited


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    product_price = fields.Float(
        'Unit Price',
        track_visibility='onchange',
    )
    fixed_asset = fields.Boolean('Fixed Asset')
    price_subtotal = fields.Float(
        'Sub Total',
        compute="_amount_line",
        store=True,
    )

    @api.depends('product_qty', 'product_price')
    def _amount_line(self):
        self.price_subtotal = self.product_qty * self.product_price
