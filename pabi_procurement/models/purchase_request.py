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
        required=True,
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
    amount_untaxed = fields.Float(
        'Untaxed Amount',
        readonly=True,
        default=0.0
    )
    amount_tax = fields.Float(
        'Taxes',
        readonly=True,
        default=0.0
    )
    amount_total = fields.Float(
        'Total',
        readonly=True,
        default=0.0
    )

    @api.model
    def create(self, vals):
        create_rec = super(PurchaseRequest, self).create(vals)
        AccTax = self.env['account.tax']
        total_untaxed = 0.0
        tax_amount = 0.0
        if 'line_ids' in vals:
            if len(vals['line_ids']) > 0:
                for line_rec in vals['line_ids']:
                    field = line_rec[2]
                    for rec_taxes in field['taxes_id']:
                        for rec_tax in rec_taxes[2]:
                            domain = [('id', '=', rec_tax)]
                            found_tax = AccTax.search(domain)
                            if found_tax.type == 'percent':
                                tax_amount += field['product_qty'] * (
                                    field['price_unit'] * found_tax.amount
                                )
                            elif found_tax.type == 'fixed':
                                tax_amount += field['product_qty'] * (
                                    field['price_unit'] + found_tax.amount
                                )
                    untaxed = field['product_qty'] * field['price_unit']
                    total_untaxed += untaxed
            create_rec.amount_untaxed = total_untaxed
            create_rec.amount_tax = tax_amount
            create_rec.amount_total = total_untaxed + tax_amount
        return create_rec

    @api.multi
    def write(self, vals):
        super(PurchaseRequest, self).write(vals)
        PRLine = self.env['purchase.request.line']
        sum_total = 0.0
        total_untaxed = 0.0
        tax_amount = 0.0
        domain = [('request_id', '=', self.id)]
        found_recs = PRLine.search(domain)
        for rec in found_recs:
            for rec_tax in rec.taxes_id:
                if rec_tax.type == 'percent':
                    tax_amount += rec.product_qty * (
                        rec.price_unit * rec_tax.amount
                    )
                elif rec_tax.type == 'fixed':
                    tax_amount += rec.product_qty * (
                        rec.price_unit + rec_tax.amount
                    )
            total_untaxed += rec.product_qty * rec.price_unit
            sum_total += rec.price_subtotal
        edited = super(PurchaseRequest, self).\
            write({
                'amount_untaxed': total_untaxed,
                'amount_tax': tax_amount,
                'amount_total': sum_total,
            })
        return edited

    @api.model
    def _finalize_data_to_load(self, fields, data):
        # Case multiple order line, split lines
        if 'line_ids' in fields:
            datas = []
            is_first = True
            for line in data[fields.index('line_ids')]:
                if is_first:
                    i = fields.index('line_ids')  # Delete 'order_line'
                    del fields[i]
                    del data[i]
                    fields += ['line_ids/'+key for key in line.keys()]
                datas += [tuple(data + line.values())]
                is_first = False
            return fields, datas
        else:
            return fields, [tuple(data)]   # one line sales order

    @api.model
    def generate_purchase_request(self, data_dict):
        fields = data_dict.keys()
        data = data_dict.values()
        # Final Preparation of fields and data
        fields, data = self._finalize_data_to_load(fields, data)
        res = self.load(fields, data)
        order_id = res['ids'] and res['ids'][0] or False
        if not order_id:
            return {
                'is_success': False,
                'result': False,
                'messages': [m['message'] for m in res['messages']],
            }
        else:
            order = self.browse(order_id)
            return {
                'is_success': True,
                'result': {
                    'request_id': order.id,
                    'name': order.name,
                    'partner_id': order.partner_id.id,
                },
                'messages': False
            }


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    price_unit = fields.Float(
        'Unit Price',
        track_visibility='onchange',
    )
    fixed_asset = fields.Boolean('Fixed Asset')
    price_subtotal = fields.Float(
        'Sub Total',
        compute="_compute_price_subtotal",
        store=True,
    )
    taxes_id = fields.Many2many(
        'account.tax',
        'purchase_request_taxes_rel',
        'request_line_id',
        'tax_id',
        'Taxes'
    )

    @api.multi
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_price_subtotal(self):
        tax_amount = 0.0
        for line in self:
            amount_untaxed = line.product_qty * line.price_unit
            for line_tax in line.taxes_id:
                if line_tax.type == 'percent':
                    tax_amount += line.product_qty * (
                        line.price_unit * line_tax.amount
                    )
                elif line_tax.type == 'fixed':
                    tax_amount += line.product_qty * (
                        line.price_unit + line_tax.amount
                    )
            cur = line.request_id.currency_id
            line.price_subtotal = cur.round(amount_untaxed + tax_amount)
