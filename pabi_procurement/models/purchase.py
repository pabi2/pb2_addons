# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError
from openerp.tools import float_compare
import time


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dummy_quote_id = fields.Many2one(
        'purchase.order',
        string='Quotation Reference',
        compute='_compute_dummy_quote_id',
    )
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
    order_state = fields.Selection(
        string='PO Status',
        related='order_id.state',
        readonly=True,
    )

    @api.one
    def _compute_dummy_quote_id(self):
        self.dummy_quote_id = self.id

    @api.model
    def by_pass_approve(self, ids):
        po_rec = self.browse(ids)
        po_rec.action_button_convert_to_order()
        if po_rec.state != 'done':
            po_rec.state = 'done'
        return True

    @api.multi
    def wkf_validate_invoice_method(self):
        """ Change invoice method to 'or' when picking + service """
        for po in self:
            if po.invoice_method == 'picking' and \
                not any([l.product_id and
                         l.product_id.type in ('product', 'consu') and
                         l.state != 'cancel' for l in po.order_line]):
                po.invoice_method = 'order'
        return True

    @api.multi
    def wkf_validate_vs_requisition(self):
        """ Amount should not exceed that in Requisition """
        decimal_prec = self.env['decimal.precision']
        precision = decimal_prec.precision_get('Account')
        for po in self:
            # Quotation or Purchase Order
            requisition = po.requisition_id or po.quote_id.requisition_id
            if requisition:
                if float_compare(po.amount_total,
                                 requisition.amount_total,
                                 precision) == 1:
                    raise UserError(
                        _('Confirmed amount exceed Call for Bid amount')
                    )
        return True

    @api.multi
    def action_button_convert_to_order(self):
        self.wkf_validate_vs_requisition()
        return super(PurchaseOrder, self).action_button_convert_to_order()


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
