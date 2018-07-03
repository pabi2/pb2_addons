# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    _STATES = [
        ('draft', 'Draft'),
        ('to_approve', 'To Accept'),
        ('approved', 'Accepted'),
        ('done', 'Done'),
        ('rejected', 'Rejected')
    ]

    @api.model
    def _get_default_responsible_by(self):
        return self.env['res.users'].browse(self.env.uid)

    state = fields.Selection(
        selection=_STATES,
        copy=False,
    )
    committee_ids = fields.One2many(
        'purchase.request.committee',
        'request_id',
        string='Committee',
        readonly=False,
    )
    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Attachment',
        copy=False,
        domain=[('res_model', '=', 'purchase.request')],
    )
    date_approve = fields.Date(
        string='Approved Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
        help="Date when the request has been approved",
    )
    date_start = fields.Date(
        required=True,
    )
    responsible_uid = fields.Many2one(
        'res.users',
        string='Responsible Person',
        required=True,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
        track_visibility='onchange',
        domain=lambda self:
        [('id', 'in', self.env.ref('purchase.'
                                   'group_purchase_manager').users.ids)],
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.company_id.currency_id,
    )
    currency_rate = fields.Float(
        string='Rate',
        digits=(12, 6),
        default=1.0,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    amount_company = fields.Float(
        string='Amount (THB)',
        compute='_compute_amount_company',
    )
    objective = fields.Text(
        string='Objective',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Procurement Method',
        readonly=True,
        states={'draft': [('readonly', False)],
                'to_approve': [('readonly', False)]},
    )
    purchase_price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Price Range',
        readonly=True,
        states={'draft': [('readonly', False)],
                'to_approve': [('readonly', False)]},
    )
    purchase_condition_id = fields.Many2one(
        'purchase.condition',
        string='Condition',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_condition_detail_id = fields.Many2one(
        'purchase.condition.detail',
        string='Condition Detail',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_condition_detail = fields.Text(
        string='Condition Info',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # purchase_prototype_id = fields.Many2one(
    #     'res.project.prototype',
    #     string='Prototype',
    #     required=False,
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    # )
    prototype_type = fields.Selection(
        [('research', 'Research'),
         ('deliver', 'Deliver')],
        string='Prototype Type',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_unit_id = fields.Many2one(
        'wkf.config.purchase.unit',
        string='Procurement Unit',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    request_ref_id = fields.Many2one(
        'purchase.request',
        string='PR Reference',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    total_budget_value = fields.Float(
        'Total Budget Value',
        readonly=True,
        default=0.0,
    )
    purchase_type_id = fields.Many2one(
        'purchase.type',
        string='Procurement Type',
        readonly=True,
        states={'draft': [('readonly', False)],
                'to_approve': [('readonly', False)]},
    )
    delivery_address = fields.Text(
        string='Delivery Address',
        readonly=True,
        states={'draft': [('readonly', False)]},
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
    is_central_purchase = fields.Boolean(
        string='Central Purchase',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
        default=False,
    )
    is_small_amount = fields.Boolean(
        string='Small Amount',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
        default=False,
    )
    small_amount_reason = fields.Char(
        string='Small Amount Reason',
        readonly=True,
        copy=False,
    )
    accept_reason_txt = fields.Char(
        string='Accept Reason',
        readonly=True,
        copy=False,
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'PR Numbr must be unique!'),
    ]

    @api.multi
    def _compute_amount_company(self):
        for rec in self:
            rec.amount_company = rec.amount_total * rec.currency_rate

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
    def _prepare_data_to_load(self, fields, data):
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
                    fields += ['line_ids/' + key for key in line.keys()]
                    # collect child key index
                    for key in line.keys():
                        found_idx = fields.index('line_ids/' + key)
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
    def _add_line_data(self, fields, data):
        if 'line_ids/fund_id.id' not in fields:
            new_data = []
            for data_line in data:
                data_line = data_line + (u'NSTDA',)
                new_data.append(data_line)
            fields.append('line_ids/fund_id')
            return fields, new_data
        else:
            fund = self.env.ref('base.fund_nstda')  # NSTDA Fund
            fund_idx = fields.index('line_ids/fund_id.id')
            new_data = []
            for data_line in data:
                if not data_line[fund_idx]:
                    lst = list(data_line)
                    lst[fund_idx] = fund.id
                    data_line = tuple(lst)
                new_data.append(data_line)
            return fields, new_data

    @api.model
    def create_purchase_request_attachment(self, data_dict, pr_id):
        Employee = self.env['hr.employee']
        attachment_ids = []
        attach_data = {}
        if 'attachment_ids' in data_dict:
            PRAttachment = self.env['ir.attachment']
            file_prefix = self.env.user.company_id.pabiweb_file_prefix
            attachment_tup = data_dict['attachment_ids']
            for att_rec in attachment_tup:
                attach_data['name'] = att_rec['name']
                attach_data['description'] = att_rec['description']
                attach_data['res_id'] = pr_id
                attach_data['res_model'] = 'purchase.request'
                attach_data['type'] = 'url'
                domain = [('employee_code', '=', att_rec.get('attach_by'))]
                attach_data['attach_by'] = \
                    Employee.search(domain).user_id.id
                attach_data['url'] = file_prefix + att_rec['file_url']
                attachment = PRAttachment.create(attach_data)
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

    @api.multi
    def _validate_required_fields(self):
        # purchase_method_id, purchase_type_id, and committee_ids must exists
        _dict = {'purchase_type_id': 'Purchase Type',
                 'purchase_method_id': 'Purchase Method',
                 'purchase_price_range_id': 'Price Range',
                 'committee_ids': 'Commitee', }
        for pr in self:
            if pr.is_small_amount:
                continue
            for field in _dict.keys():
                if field in pr and not pr[field]:
                    raise ValidationError(
                        _('%s is required for %s') % (_dict[field], pr.name))

    @api.multi
    def button_approved(self):
        self._validate_required_fields()
        res = super(PurchaseRequest, self).button_approved()
        PWInterface = self.env['purchase.web.interface']
        PWInterface.send_pbweb_action_request(self, 'accept')
        return res

    @api.multi
    def button_to_approve(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(
                    _(('You cannot confirm a request without any line.')))
        res = super(PurchaseRequest, self).button_to_approve()
        return res

    @api.multi
    def button_rejected(self):
        res = super(PurchaseRequest, self).button_rejected()
        PWInterface = self.env['purchase.web.interface']
        PWInterface.send_pbweb_action_request(self, 'cancel')
        return res

    @api.multi
    def button_agree_and_done(self):
        self.write({'state': 'done'})
        PWInterface = self.env['purchase.web.interface']
        PWInterface.send_pbweb_action_request(self, 'agree_and_done')
        return True


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

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
    responsible_uid = fields.Many2one(
        'res.users',
        string='Responsible Person',
        related='request_id.responsible_uid',
        store=True,
        readonly=True,
    )
    date_required = fields.Date(
        string='Scheduled Date',
    )
    is_central_purchase = fields.Boolean(
        string='Is Central Purchase',
        readonly=True,
        related='request_id.is_central_purchase',
        store=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        'Fiscal Year',
        readonly=True,
    )
    state = fields.Selection(
        [('open', 'Open'),
         ('close', 'Closed'),
         ],
        string='Status',
        track_visibility='onchange',
        required=True,
        default='open',
    )

    @api.one
    @api.depends('requisition_lines.requisition_id.state')
    def _get_requisition_state(self):
        self.requisition_state = 'none'
        if self.requisition_lines:
            if any([pr_line.requisition_id.state == 'done' for
                    pr_line in
                    self.requisition_lines]):
                self.requisition_state = 'done'
            elif all([pr_line.requisition_id.state == 'cancel'
                      for pr_line in self.requisition_lines]):
                self.requisition_state = 'none'
            elif any([pr_line.requisition_id.state == 'in_progress'
                      for pr_line in self.requisition_lines]):
                self.requisition_state = 'in_progress'
            elif all([pr_line.requisition_id.state in ('draft', 'cancel')
                      for pr_line in self.requisition_lines]):
                self.requisition_state = 'draft'

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

    @api.multi
    def write(self, vals):
        """ If all pr line's state are close, also set PR to Done """
        res = super(PurchaseRequestLine, self).write(vals)
        if 'state' in vals and vals['state'] == 'close':
            for rec in self:
                if rec.request_id.state == 'done':
                    continue
                pr_line_states = rec.request_id.line_ids.mapped('state')
                if len(pr_line_states) == 1 and pr_line_states[0] == 'close':
                    rec.request_id.write({'state': 'done'})
        return res


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
        required=True,
    )
    position = fields.Char(
        string='Position',
    )
    committee_type_id = fields.Many2one(
        'purchase.committee.type',
        string='Type',
    )
    request_id = fields.Many2one(
        'purchase.request',
        string='Purchase Request',
    )
