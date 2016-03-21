# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    _BID_TYPE = {
        ('regular', 'ซื้อ/จ้าง/เช่า'),
        ('consult', 'จ้างที่ปรึกษา'),
        ('design', 'จ้างออกแบบ'),
        ('estate', 'เช่าอสังหาริมทรัพย์'),
    }

    _METHOD = {
        ('method1', 'ราคาไม่เกิน 30,000 บาท'),
        ('method2', 'Method 2'),
        ('method3', 'Method 3'),
        ('method4', 'Method 4'),
    }

    bid_type = fields.Selection(_BID_TYPE, string="Type")
    description = fields.Text(string='Description')
    objective = fields.Text(string='Objective')
    total_budget_value = fields.Float('Total Budget Value')
    original_durable_articles = fields.Boolean(
        string='Prototype',
        default=False,
        track_visibility='onchange',
    )
    procure_method = fields.Selection(
        selection=_METHOD,
        string='Procurement Method',
        default='method1',
        track_visibility='onchange',
        required=True
    )
    currency_id = fields.Many2one('res.currency', 'Currency')
    currency_rate = fields.Float('Rate')
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
    amount_total = fields.Float(
        'Total',
        readonly=True,
        default=0,
    )
    approval_document_no = fields.Char(string="No.")
    approval_document_date = fields.Date(string="Date")
    approval_document_header = fields.Text(string="Header")
    approval_document_footer = fields.Text(string="Footer")

    @api.model
    def create(self, vals):
        create_rec = super(PurchaseRequisition, self).create(vals)
        sum_total = 0
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
        sum_total = 0
        domain = [('requisition_id', '=', self.id)]
        found_recs = prql_obj.search(domain)
        for rec in found_recs:
            sum_total += rec.product_qty * rec.price_unit
        edited = super(PurchaseRequisition, self).\
            write({'amount_total': sum_total})
        return edited


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

    @api.onchange('product_qty', 'price_unit')
    @api.depends('product_qty', 'price_unit')
    def _amount_line(self):
        self.price_subtotal = self.product_qty * self.price_unit
