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
                    sum_total += field['product_qty'] * field['price_unit']
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
            sum_total += rec.product_qty * rec.price_unit
        edited = super(PurchaseRequest, self).\
            write({'amount_total': sum_total})
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
            return {'is_success': False, 'result': False,
                    'messages': [m['message'] for m in res['messages']]}
        else:
            order = self.browse(order_id)
            return {'is_success': True, 'result': {'request_id': order.id,
                                                   'name': order.name,
                                                   'partner_id':order.name,
                                                   },
                    'messages': False}


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

    @api.multi
    @api.depends('product_qty', 'price_unit')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.product_qty * rec.price_unit
