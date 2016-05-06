# -*- coding: utf-8 -*-

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
import time


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    _STATES = [
        ('draft', 'Draft'),
        ('in_progress', 'Confirmed'),
        ('verify', 'To Verify'),
        ('rejected', 'Rejected'),
        ('open', 'Bid Selection'),
        ('done', 'PO Created'),
        ('cancel', 'Cancelled'),
    ]

    state = fields.Selection(
        _STATES,
        string='Status',
        track_visibility='onchange',
        required=True,
        copy=False,
    )
    purchase_type_id = fields.Many2one(
        'purchase.type',
        string='Type',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    objective = fields.Text(
        string='Objective',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    total_budget_value = fields.Float(
        string='Total Budget Value',
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_prototype_id = fields.Many2one(
        'purchase.prototype',
        string='Prototype',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Method',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    currency_rate = fields.Float(
        string='Rate',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    committee_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        string='Committee',
        readonly=False,
    )
    committee_tor_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        string='Committee TOR',
        readonly=False,
        domain=[
            ('committee_type', '=', 'tor'),
        ],
    )
    committee_tender_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        string='Committee Tender',
        readonly=False,
        domain=[
            ('committee_type', '=', 'tender'),
        ],
    )
    committee_receipt_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        string='Committee Receipt',
        readonly=False,
        domain=[
            ('committee_type', '=', 'receipt'),
        ],
    )
    committee_std_price_ids = fields.One2many(
        'purchase.requisition.committee',
        'requisition_id',
        string='Committee Standard Price',
        readonly=False,
        domain=[
            ('committee_type', '=', 'std_price'),
        ],
    )
    attachment_ids = fields.One2many(
        'purchase.requisition.attachment',
        'requisition_id',
        string='Attach Files',
    )
    amount_untaxed = fields.Float(
        string='Untaxed Amount',
        compute='_compute_amount',
        store=True,
        readonly=True,
        default=0.0,
    )
    amount_tax = fields.Float(
        string='Taxes',
        compute='_compute_amount',
        store=True,
        readonly=True,
        default=0.0,
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount',
        store=True,
        readonly=True,
        default=0.0,
    )
    approval_document_no = fields.Char(
        string='No.',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    approval_document_date = fields.Date(
        string='Date of Approval',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Date of the order has been approved ",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    approval_document_header = fields.Text(
        string='Header',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    approval_document_footer = fields.Text(
        string='Footer',
    )
    reject_reason_txt = fields.Char(
        string="Rejected Reason",
        readonly=True,
        copy=False,
    )
    is_central_purchase = fields.Boolean(
        string='Central Purchase',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=False,
    )

    @api.one
    @api.depends('line_ids.price_subtotal', 'line_ids.tax_ids')
    def _compute_amount(self):
        amount_untaxed = 0.0
        amount_tax = 0.0
        for line in self.line_ids:
            taxes = line.tax_ids.compute_all(line.price_unit, line.product_qty,
                                             product=line.product_id)
            amount_tax += sum([tax['amount'] for tax in taxes['taxes']])
            amount_untaxed += taxes['total']
        self.amount_untaxed = amount_untaxed
        self.amount_tax = amount_tax
        self.amount_total = amount_untaxed + amount_tax

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

    @api.model
    def _prepare_purchase_order_line(self, requisition, requisition_line,
                                     purchase_id, supplier):
        res = super(PurchaseRequisition, self).\
            _prepare_purchase_order_line(requisition, requisition_line,
                                         purchase_id, supplier)
        # Always use price and tax_ids from pr_line (NOT from product)
        res.update({
            'name': requisition_line.product_name,
            'price_unit': requisition_line.price_unit,
            'taxes_id': [(6, 0, requisition_line.tax_ids.ids)],
        })
        return res

    @api.multi
    def to_verify(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        self.state = 'verify'
        return True

    @api.multi
    def rejected(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        self.signal_workflow('rejected')
        self.state = 'rejected'


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    price_unit = fields.Float(
        string='Unit Price',
    )
    price_standard = fields.Float(
        string='Standard Price',
    )
    fixed_asset = fields.Boolean(
        string='Fixed Asset',
        default=False,
    )
    price_subtotal = fields.Float(
        string='Sub Total',
        compute="_compute_price_subtotal",
        store=True,
        digits_compute=dp.get_precision('Account')
    )
    tax_ids = fields.Many2many(
        'account.tax',
        'purchase_requisition_taxes_rel',
        'requisition_line_id',
        'tax_id',
        string='Taxes',
        readonly=False,  # TODO: readonly=True
    )
    order_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line'
    )
    product_name = fields.Char(
        string='Description',
    )

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
            if 'product_uom_id' in res['value']:
                del res['value']['product_uom_id']
        return res

    @api.multi
    @api.depends('product_qty', 'price_unit', 'tax_ids')
    def _compute_price_subtotal(self):
        tax_amount = 0.0
        for line in self:
            amount_untaxed = line.product_qty * line.price_unit
            for line_tax in line.tax_ids:
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


class PurchaseRequisitionAttachment(models.Model):
    _name = 'purchase.requisition.attachment'
    _description = 'Purchase Requisition Attachment'

    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Purchase Requisition',
    )
    name = fields.Char(
        string='File Name',
    )
    description = fields.Char(
        string='File Description',
    )
    file_url = fields.Char(
        string='File Url',
    )
    file = fields.Binary(
        string='File',
    )


class PurchaseRequisitionCommittee(models.Model):
    _name = 'purchase.requisition.committee'
    _description = 'Purchase Requisition Committee'
    _order = 'sequence, id'

    _COMMITTEE_TYPE = [
        ('tor', 'TOR'),
        ('tender', 'Tender'),
        ('receipt', 'Receipt'),
        ('std_price', 'Standard Price')
    ]

    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Purchase Requisition',
    )
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
    committee_type = fields.Selection(
        string='Type',
        selection=_COMMITTEE_TYPE,
    )
