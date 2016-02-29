# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
import openerp.addons.decimal_precision as dp
import time


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    _REASON = {
        ('reason1', 'Reason 1'),
        ('reason2', 'Reason 2'),
        ('reason3', 'Reason 3'),
        ('reason4', 'Reason 4'),
    }
    _METHOD = {
        ('method1', 'Method 1'),
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

    committee_ids = fields.One2many('procurement.committee', 'pr_id',
                                    'Committee to Procure',
                                    readonly=False,
                                    track_visibility='onchange')
    attachment_ids = fields.One2many('procurement.attachment', 'pr_id',
                                     'Attach Files',
                                     readonly=False,
                                     track_visibility='onchange')
    assigned_to = fields.Many2one('res.users', 'Approver',
                                  readonly=True,
                                  track_visibility='onchange')
    date_approved = fields.Date('Request date',
                                help="Date when the request has been approved",
                                default=lambda *args:
                                time.strftime('%Y-%m-%d %H:%M:%S'),
                                readonly=True,
                                track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', 'Currency')
    currency_rate = fields.Float('Rate')
    procure_reason = fields.Selection(selection=_REASON,
                                      string='Reason',
                                      track_visibility='onchange',
                                      required=True)
    objective = fields.Char('Objective')
    procure_method = fields.Selection(selection=_METHOD,
                                      string='Procurement Method',
                                      track_visibility='onchange',
                                      required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    procure_type = fields.Selection(selection=_TYPE,
                                    string='Type',
                                    track_visibility='onchange',
                                    required=True)


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    product_price = fields.Float('Unit Price',
                                 track_visibility='onchange',
                                 digits_compute=dp.get_precision(
                                     'Product Price'))
