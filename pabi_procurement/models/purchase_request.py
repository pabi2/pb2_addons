# -*- coding: utf-8 -*-

from openerp import fields, models, api, _


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    _STATES = [
        ('draft', 'Draft'),
        ('to_approve', 'To Accept'),
        ('approved', 'Accepted'),
        ('rejected', 'Cancelled')
    ]

    _SEMINAR = [
        ('1', 'from myProject'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]

    state = fields.Selection(
        selection=_STATES,
    )
    committee_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        string='Committee',
        readonly=False,
    )
    committee_tor_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        string='Committee TOR',
        readonly=False,
        domain=[
            ('committee_type', '=', 'tor'),
        ],
    )
    committee_tender_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        string='Committee Tender',
        readonly=False,
        domain=[
            ('committee_type', '=', 'tender'),
        ],
    )
    committee_receipt_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        string='Committee Receipt',
        readonly=False,
        domain=[
            ('committee_type', '=', 'receipt'),
        ],
    )
    committee_std_price_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        string='Committee Standard Price',
        readonly=False,
        domain=[
            ('committee_type', '=', 'std_price'),
        ],
    )
    attachment_ids = fields.One2many(
        'purchase.request.attachment',
        'request_id',
        string='Attach Files',
        readonly=False,
    )
    date_approved = fields.Date(
        string='Approved Date',
        readonly=False,  # TODO: False for testing, True when live.
        track_visibility='onchange',
        help="Date when the request has been approved",
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        track_visibility='onchange',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
    )
    currency_rate = fields.Float(
        string='Rate',
        digits=(12, 6),
    )
    objective = fields.Text(
        string='Objective',
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Procurement Method',
    )
    purchase_prototype_id = fields.Many2one(
        'purchase.prototype',
        string='Prototype',
    )
    purchase_unit_id = fields.Many2one(
        'purchase.unit',
        string='Procurement Unit',
    )
    request_ref_id = fields.Many2one(
        'purchase.request',
        string='PR Reference',
    )
    seminar_id = fields.Selection(
        selection=_SEMINAR,
        string='Seminar',
        default='1',
    )
    total_budget_value = fields.Float(
        'Total Budget Value',
        default=0.0,
    )
    purchase_type_id = fields.Many2one(
        'purchase.type',
        string='Procurement Type',
    )
    delivery_address = fields.Text(
        string='Delivery Address',
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
    def call_gen_pr(self):
        # for testing generate pr
        gen_dict = {
            'name': u'PR0000001',
            'requested_by': u'Administrator',
            'responsible_user_id': u'Administrator',
            'date_approved': u'2016-01-31',
            'prototype': u'True',
            'total_budget_value': u'240000',
            'purchase_type_id': u'AAAA',
            'purchase_method_id': u'AAAA',
            'description': u'Put your PR description here.',
            'objective': u'Put your PR objective here',
            'currency_id': u'THB',
            'currency_rate': u'1',
            'delivery_address': u'Put your PR delivery address here',
            'date_start': u'2016-01-31',
            'picking_type_id': u'Receipts',
            'operating_unit_id': u'Main Operating Unit',
            'line_ids': (
                {
                    'name': u'Computer',
                    'product_qty': u'20',
                    'price_unit': u'10000',
                    'date_required': u'2016-01-31',
                    'tax_ids': u'Tax 7.00%',
                },
                {
                    'name': u'HDD',
                    'product_qty': u'20',
                    'price_unit': u'1030',
                    'date_required': u'2016-01-31',
                    'tax_ids': u'Tax 7.00%',
                }
            ),
            'attachment_ids': (
                {
                    'name': u'PD Form',
                    'file_url': u'google.com',
                },
                {
                    'name': u'PD Form2',
                    'file_url': u'google.com',
                },
                {
                    'name': u'PD Form2',
                    'file_url': u'google.com',
                },
            ),
            'committee_ids': (
                {
                    'name': u'Mr. Steve Roger',
                    'position': u'Manager',
                    'responsible': u'Responsible',
                    'committee_type': u'tor',
                    'sequence': u'1',
                },
                {
                    'name': u'Mr. Samuel Jackson',
                    'position': u'Staff',
                    'responsible': u'Responsible',
                    'committee_type': u'tor',
                    'sequence': u'1',
                },
                {
                    'name': u'Mr. Steve Roger',
                    'position': u'Manager',
                    'responsible': u'Responsible',
                    'committee_type': u'receipt',
                    'sequence': u'1',
                },
                {
                    'name': u'Mr. Samuel Jackson',
                    'position': u'Staff',
                    'responsible': u'Responsible',
                    'committee_type': u'std_price',
                    'sequence': u'1',
                },
            ),
        }
        self.generate_purchase_request(gen_dict)
        return True

    @api.model
    def _finalize_data_to_load(self, fields, data):
        # clear up attachment and committee data. will and them after create pr
        clear_up_fields = [
            'attachment_ids',
            'committee_ids'
        ]
        for clear_up_field in clear_up_fields:
            if clear_up_field in fields:
                i = fields.index(clear_up_field)
                del fields[i]
                del data[i]
        if 'line_ids' in fields:
            line_ids_index = []
            datas = []
            arrange_dat = []
            dat_tuple = ()
            is_first = True
            for line in data[fields.index('line_ids')]:
                if is_first:
                    i = fields.index('line_ids')
                    del fields[i]
                    del data[i]
                    fields += ['line_ids/'+key for key in line.keys()]
                    # collect child key index
                    for key in line.keys():
                        found_idx = fields.index('line_ids/'+key)
                        if found_idx:
                            line_ids_index.append(found_idx)
                datas += [tuple(data + line.values())]
                is_first = False
            # clear header data in line row
            is_first = True
            for line_dat in enumerate(datas):
                if is_first:
                    is_first = False
                    arrange_dat.append(line_dat[1])
                    continue
                for col_dat in enumerate(line_dat[1]):
                    if col_dat[0] not in line_ids_index:
                        dat_tuple += (u'',)
                    else:
                        dat_tuple += (col_dat[1],)
                arrange_dat.append(dat_tuple)
                dat_tuple = ()
            return fields, arrange_dat
        else:
            return fields, [tuple(data)]   # one line sales order

    @api.model
    def create_purchase_request_attachment(self, data_dict, pr_id):
        attachment_ids = []
        if 'attachment_ids' in data_dict:
            PRAttachment = self.env['purchase.request.attachment']
            attachment_tup = data_dict['attachment_ids']
            for att_rec in attachment_tup:
                att_rec['request_id'] = pr_id
                attachment = PRAttachment.create(att_rec)
                attachment_ids.append(attachment.id)
        return attachment_ids

    @api.model
    def create_purchase_request_committee(self, data_dict, pr_id):
        commitee_ids = []
        if 'committee_ids' in data_dict:
            PRCommittee = self.env['purchase.request.committee']
            committee_tup = data_dict['committee_ids']
            for cmt_rec in committee_tup:
                cmt_rec['request_id'] = pr_id
                commitee = PRCommittee.create(cmt_rec)
                commitee_ids.append(commitee.id)
        return commitee_ids

    @api.model
    def generate_purchase_request(self, data_dict):
        fields = data_dict.keys()
        data = data_dict.values()
        # Final Preparation of fields and data
        fields, data = self._finalize_data_to_load(fields, data)
        load_res = self.load(fields, data)
        res_id = load_res['ids'] and load_res['ids'][0] or False
        if not res_id:
            return {
                'is_success': False,
                'result': False,
                'messages': [m['message'] for m in load_res['messages']],
            }
        else:
            # TODO: https://mobileapp.nstda.or.th/redmine/issues/326
            res = self.browse(res_id)
            attachment = self.create_purchase_request_attachment(data_dict,
                                                                 res_id)
            committee = self.create_purchase_request_committee(data_dict,
                                                               res_id)
            if not attachment or not committee:
                return {
                    'is_success': False,
                    'result': False,
                    'messages': _('Error on create attachment '
                                  'or committee list'),
                }
            else:
                return {
                    'is_success': True,
                    'result': {
                        'request_id': res.id,
                        'name': res.name,
                    },
                    'messages': _('PR has been created.'),
                }


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    price_unit = fields.Float(
        string='Unit Price',
        track_visibility='onchange',
    )
    fixed_asset = fields.Boolean(
        string='Fixed Asset',
    )
    price_subtotal = fields.Float(
        string='Sub Total',
        compute="_compute_price_subtotal",
        store=True,
    )
    tax_ids = fields.Many2many(
        'account.tax',
        'purchase_request_taxes_rel',
        'request_line_id',
        'tax_id',
        string='Taxes',
        readonly=False,  # TODO: readonly=True
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Person',
        related='request_id.responsible_user_id',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('product_qty', 'price_unit', 'tax_ids')
    def _compute_price_subtotal(self):
        for rec in self:
            taxes = rec.tax_ids.compute_all(rec.price_unit, rec.product_qty,
                                            product=rec.product_id)
            rec.price_subtotal = taxes['total']
            if rec.request_id:
                rec.price_subtotal = \
                    rec.request_id.currency_id.round(rec.price_subtotal)


class PurchaseRequestAttachment(models.Model):
    _name = 'purchase.request.attachment'
    _description = 'Purchase Request Attachment'

    request_id = fields.Many2one(
        'purchase_request',
        string='Purchase Request',
    )
    name = fields.Char(
        string='File Name',
    )
    file_url = fields.Char(
        string='File Url',
    )
    file = fields.Binary(
        string='File',
    )


class PurchaseRequestCommittee(models.Model):
    _name = 'purchase.request.committee'
    _description = 'Purchase Request Committee'
    _order = 'sequence, id'

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
        required=True,
    )
    request_id = fields.Many2one(
        'purchase_request',
        string='Purchase Request',
    )
