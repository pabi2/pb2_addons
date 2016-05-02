# -*- coding: utf-8 -*-

from openerp import fields, models, api
import time
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_reference = fields.Date(
        string='Reference Date',
        default=fields.Date.today(),
        readonly=True,
        track_visibility='onchange',
    )
    mycontract_id = fields.Selection(
        selection=[
            ('1', 'from myContract'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
        ],
        string='myContract',
        default='1',
    )
    fine_condition = fields.Selection(
        selection=[
            ('day', 'Day'),
            ('date', 'Date'),
            ('manual', 'Manual'),
        ],
        string='Fine Condition',
        default='day',
        Required=True,
    )
    fine_by_date = fields.Date(
        string='Fine Date',
        default=fields.Date.today(),
    )
    fine_by_num_of_days = fields.Integer(
        string='No. of Days',
        default=15,
    )
    fine_by_manual_rate = fields.Float(
        string='Manual Rate',
        default=1.0,
    )
    fine_rate = fields.Float(
        string='Fine Rate',
        default=0.1,
    )
    date_contract_start = fields.Date(
        string='Contract Start Date',
        default=fields.Date.today(),
        track_visibility='onchange',
    )
    committee_ids = fields.One2many(
        'purchase.order.committee',
        'order_id',
        string='Committee',
        readonly=False,
    )
    committee_tor_ids = fields.One2many(
        'purchase.order.committee',
        'order_id',
        string='Committee TOR',
        readonly=False,
        domain=[
            ('committee_type', '=', 'tor'),
        ],
    )
    committee_tender_ids = fields.One2many(
        'purchase.order.committee',
        'order_id',
        string='Committee Tender',
        readonly=False,
        domain=[
            ('committee_type', '=', 'tender'),
        ],
    )
    committee_receipt_ids = fields.One2many(
        'purchase.order.committee',
        'order_id',
        string='Committee Receipt',
        readonly=False,
        domain=[
            ('committee_type', '=', 'receipt'),
        ],
    )
    committee_std_price_ids = fields.One2many(
        'purchase.order.committee',
        'order_id',
        string='Committee Standard Price',
        readonly=False,
        domain=[
            ('committee_type', '=', 'std_price'),
        ],
    )
    create_by = fields.Many2one(
        'res.users',
        string='Create By',
    )
    verified_by = fields.Many2one(
        'res.users',
        string='Verified By',
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
    )
    position = fields.Char(
        string='Position',
    )
    date_approval = fields.Date(
        string='Approved Date',
        help="Date when the PO has been approved",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        readonly=True,
        track_visibility='onchange',
    )
    acceptance_ids = fields.One2many(
        'purchase.work.acceptance',
        'order_id',
        string='Acceptance',
        readonly=False,
    )

    @api.model
    def by_pass_approve(self, ids):
        po_rec = self.browse(ids)
        po_rec.action_button_convert_to_order()
        if po_rec.state != 'done':
            po_rec.state = 'done'
        return True


class PurchaseType(models.Model):
    _name = 'purchase.type'
    _description = 'PABI2 Purchase Type'

    name = fields.Char(
        string='Purchase Type',
    )


class PurchasePrototype(models.Model):
    _name = 'purchase.prototype'
    _description = 'PABI2 Purchase Prototype'

    name = fields.Char(
        string='Prototype',
    )


class PurchaseMethod(models.Model):
    _name = 'purchase.method'
    _description = 'PABI2 Purchase Method'

    name = fields.Char(
        string='Purchase Method',
    )


class PurchaseUnit(models.Model):
    _name = 'purchase.unit'
    _description = 'PABI2 Purchase Unit'

    name = fields.Char(
        string='Purchase Unit',
    )


class PurchaseOrderCommittee(models.Model):
    _name = 'purchase.order.committee'
    _description = 'Purchase Order Committee'

    _COMMITTEE_TYPE = [
        ('tor', 'TOR'),
        ('tender', 'Tender'),
        ('receipt', 'Receipt'),
        ('std_price', 'Standard Price')
    ]

    sequence = fields.Integer(
        string='Sequence',
        default=1,
    )
    name = fields.Char(
        string='Name',
    )
    position = fields.Char(
        string='Position',
    )
    responsible = fields.Char(
        string='Responsible',
    )
    committee_type = fields.Selection(
        string='Type',
        selection=_COMMITTEE_TYPE,
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )


class PurchaseWorkAcceptance(models.Model):
    _name = 'purchase.work.acceptance'
    _description = 'Purchase Work Acceptance'

    name = fields.Char(
        string="Acceptance No.",
    )
    total_fine = fields.Float(
        string="Total Fine",
    )
    acceptance_line = fields.One2many(
        'purchase.work.acceptance.line',
        'acceptance_id',
        string='Work Acceptance',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )


class PurchaseWorkAcceptanceLine(models.Model):
    _name = 'purchase.work.acceptance.line'
    _description = 'Purchase Work Acceptance Line'

    acceptance_id = fields.Many2one(
        'purchase.work.acceptance',
        string='Acceptance Reference',
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    balance_qty = fields.Float(
        string='Balance Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        readonly=True,
        required=True,
    )
    to_receive_qty = fields.Float(
        string='To Receive Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='UoM',
    )
