# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError
from openerp.tools import float_compare


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
    create_by = fields.Many2one(
        'res.users',
        string='Created By',
    )
    verify_uid = fields.Many2one(
        'res.users',
        string='Verified by',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_verify = fields.Date(
        string='Verified Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Date when the request has been verified",
    )
    date_doc_approve = fields.Date(
        string='Approved Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Date of the PD has been approved ",
    )
    doc_approve_uid = fields.Many2one(
        'res.users',
        string='Approved by',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    doc_no = fields.Char(
        string='No.',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    position = fields.Char(
        string='Position',
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
        po_rec.order_id.committee_ids = po_rec.committee_ids
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


class Purchase(models.Model):
    _name = 'purchase.method'
    _description = 'PABI2 Purchase Method'

    name = fields.Char(
        string='Purchase Method',
    )


class PRWebPurchaseMethod(models.Model):
    _name = 'prweb.purchase.method'
    _description = 'PRWeb Purchase Method'

    type_id = fields.Many2one(
        'purchase.type',
        string='Type',
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Method',
    )
    price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Price Range',
    )
    condition_id = fields.Many2one(
        'purchase.condition',
        string='Condition',
    )
    confidential_id = fields.Many2one(
        'purchase.confidential',
        string='Confidential',
    )


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


class PurchaseCommitteeType(models.Model):
    _name = 'purchase.committee.type'
    _description = 'PABI2 Purchase Committee Type'

    name = fields.Char(
        string='Purchase Committee Type',
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Method',
    )

class PurchasePriceRange(models.Model):
    _name = 'purchase.price.range'
    _description = 'PABI2 Price Range'

    name = fields.Char(
        string='Purchase Price Range',
    )


class PurchaseCondition(models.Model):
    _name = 'purchase.condition'
    _description = 'PABI2 Purchase Condition'

    name = fields.Char(
        string='Purchase Condition',
    )


class PurchaseConfidential(models.Model):
    _name = 'purchase.confidential'
    _description = 'PABI2 Purchase Confidential'

    name = fields.Char(
        string='Purchase Confidential',
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
    committee_type_id = fields.Many2one(
        'purchase.committee.type',
        string='Type',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
