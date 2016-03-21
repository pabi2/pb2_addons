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
    _METHOD = {
        ('method1', 'ราคาไม่เกิน 30,000 บาท'),
        ('method2', 'Method 2'),
        ('method3', 'Method 3'),
        ('method4', 'Method 4'),
    }
    _TYPE = {
        ('regular', 'ซื้อ/จ้าง/เช่า'),
        ('consult', 'จ้างที่ปรึกษา'),
        ('design', 'จ้างออกแบบ'),
        ('estate', 'เช่าอสังหาริมทรัพย์'),
    }

    state = fields.Selection(
        selection=_STATES,
        string='Status',
        track_visibility='onchange',
        required=True,
        default='draft',
    )

    committee_ids = fields.One2many(
        'procurement.committee',
        'pr_id',
        'Committee to Procure',
        readonly=False,
        track_visibility='onchange',
    )
    attachment_ids = fields.One2many(
        'procurement.attachment',
        'pr_id',
        'Attach Files',
        readonly=False,
        track_visibility='onchange',
    )
    date_approved = fields.Date(
        'Approved Date',
        help="Date when the request has been approved",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        readonly=True,
        track_visibility='onchange',
    )
    responsible_man = fields.Many2one(
        'res.users',
        'Responsible Man',
        track_visibility='onchange',
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
    )
    currency_rate = fields.Float('Rate')
    objective = fields.Char('Objective')
    procure_method = fields.Selection(
        selection=_METHOD,
        string='Procurement Method',
        track_visibility='onchange',
        default='method1',
        required=True,
    )
    original_durable_articles = fields.Boolean(
        string='Prototype',
        default=False,
        track_visibility='onchange',
    )
    total_budget_value = fields.Float('Total Budget Value')
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Warehouse',
    )
    procure_type = fields.Selection(
        selection=_TYPE,
        string='Type',
        track_visibility='onchange',
        required=True,
    )
    delivery_address = fields.Text('Delivery Address')
    amount_total = fields.Float(
        'Total',
        readonly=True,
        default=0
    )

    @api.model
    def create(self, vals):
        create_rec = super(PurchaseRequest, self).create(vals)
        sum_total = 0
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
        sum_total = 0
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

    @api.onchange('product_qty', 'product_price')
    @api.depends('product_qty', 'product_price')
    def _amount_line(self):
        self.price_subtotal = self.product_qty * self.product_price
