# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
import openerp.addons.decimal_precision as dp
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
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('type3', 'Type 3'),
        ('type4', 'Type 4'),
    }

    state = fields.Selection(selection=_STATES,
                             string='Status',
                             track_visibility='onchange',
                             required=True,
                             default='draft')

    committee_ids = fields.One2many('procurement.committee', 'pr_id',
                                    'Committee to Procure',
                                    readonly=False,
                                    track_visibility='onchange')
    attachment_ids = fields.One2many('procurement.attachment', 'pr_id',
                                     'Attach Files',
                                     readonly=False,
                                     track_visibility='onchange')
    date_approved = fields.Date('Approved Date',
                                help="Date when the request has been approved",
                                default=lambda *args:
                                time.strftime('%Y-%m-%d %H:%M:%S'),
                                readonly=True,
                                track_visibility='onchange')
    responsible_man = fields.Many2one('res.users', 'Responsible Man',
                                      track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', 'Currency')
    currency_rate = fields.Float('Rate')
    objective = fields.Char('Objective')
    procure_method = fields.Selection(selection=_METHOD,
                                      string='Procurement Method',
                                      track_visibility='onchange',
                                      required=True)
    original_durable_articles = fields.Boolean(
        default=False,
        track_visibility='onchange',
        required=True)
    total_budget_value = fields.Float('Total Budget Value')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    procure_type = fields.Selection(selection=_TYPE,
                                    string='Type',
                                    track_visibility='onchange',
                                    required=True)
    delivery_address = fields.Text('Delivery Address')


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    product_price = fields.Float('Unit Price',
                                 track_visibility='onchange',
                                 digits_compute=dp.get_precision(
                                     'Product Price'))
