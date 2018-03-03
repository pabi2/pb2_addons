# -*- coding: utf-8 -*-
import openerp
import base64
import time
import re
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools import float_compare


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
    description = fields.Text(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    total_budget_value = fields.Float(
        string='Total Budget Value',
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # purchase_prototype_id = fields.Many2one(
    #     'res.project.prototype',
    #     string='Prototype',
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
    purchase_method_id = fields.Many2one(
        'purchase.method',
        string='Method',
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    purchase_price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Price Range',
        readonly=True,
        states={'draft': [('readonly', False)]},
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
    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Attachment',
        copy=False,
        domain=[('res_model', '=', 'purchase.requisition')],
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
    request_uid = fields.Many2one(
        'res.users',
        string='PR. Requested by',
        readonly=True,
    )
    assign_uid = fields.Many2one(
        'res.users',
        string='PR. Approver',
        readonly=True,
    )
    date_approve = fields.Date(
        string='PR. Approved Date',
        readonly=True,
        help="Date when the request has been approved",
    )
    request_ref_id = fields.Many2one(
        'purchase.request',
        string='PR Reference',
        copy=False,
        readonly=True,
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
        string='Date of Approval',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Date of the order has been approved ",
    )
    doc_approve_uid = fields.Many2one(
        'res.users',
        string='Approver',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    doc_no = fields.Char(
        string='Approval No.',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    doc_header = fields.Text(
        string='Dear,',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'done': [('readonly', False)],
        },
    )
    doc_body = fields.Text(
        string='Body',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'done': [('readonly', False)],
        },
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
    exclusive = fields.Selection(
        default='exclusive',
    )
    name = fields.Char(
        default=lambda self:
        self.env['ir.sequence'].get('purchase.requisition'),
    )
    delivery_address = fields.Text(
        string='Delivery Address',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    purchase_ids = fields.One2many(
        domain=[('order_type', '=', 'quotation')],
    )
    sent_pbweb = fields.Boolean(
        string='Is sent to PABI Web',
        default=False,
    )
    require_rfq = fields.Boolean(
        string='Require for RFQs',
        related='purchase_method_id.require_rfq',
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

    @api.onchange('is_central_purchase')
    def _onchange_is_central_purchase(self):
        # domain = []
        if self.is_central_purchase:
            self.exclusive = 'multiple'
            self.multiple_rfq_per_supplier = True
            # domain = []
        else:
            self.exclusive = 'exclusive'
            self.multiple_rfq_per_supplier = False
            # domain = self.env['operating.unit']._ou_domain()
        # return {'domain': {'operating_unit_id': domain}}

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

    # @api.multi
    # def by_pass_approve(self):
    #     po_obj = self.env["purchase.order"]
    #     po_obj.action_button_convert_to_order()
    #     return True

    @api.multi
    def create_approval_no(self):
        for rec in self:
            doc_no = self.env['ir.sequence'].get('approval.report'),
            rec.doc_no = doc_no[0]

    @api.model
    def _prepare_committee_line(self, line, order_id):
        return {
            'order_id': order_id,
            'name': line.name,
            'sequence': line.sequence,
            'position': line.position,
            'committee_type_id': line.committee_type_id.id,
        }

    @api.model
    def _prepare_order_committees(self, order_id):
        committees = []
        for line in self.committee_ids:
            committee_line = self._prepare_committee_line(line,
                                                          order_id)
            committees.append([0, False, committee_line])
        return committees

    @api.multi
    def make_purchase_order(self, partner_id):
        res = super(PurchaseRequisition, self).\
            make_purchase_order(partner_id)
        Order = self.env['purchase.order']
        for order_id in res.itervalues():
            orders = Order.search([('id', '=', order_id)])
            for order in orders:
                order.write({
                    'committee_ids': self._prepare_order_committees(order_id),
                    'verify_uid': self.verify_uid.id,
                    'date_verify': self.date_verify,
                    'doc_no': self.doc_no,
                })
        return res

    @api.model
    def _prepare_purchase_order(self, requisition, supplier):
        res = super(PurchaseRequisition, self).\
            _prepare_purchase_order(requisition, supplier)
        ou_address = requisition.operating_unit_id.partner_id
        combined_address = "%s\n%s %s %s %s\n%s" % (
            ou_address.street.strip()
            if ou_address.street else '',
            ou_address.township_id.name.strip()
            if ou_address.township_id else '',
            ou_address.district_id.name.strip()
            if ou_address.district_id else '',
            ou_address.province_id.name.strip()
            if ou_address.province_id else '',
            ou_address.zip.strip()
            if ou_address.zip else '',
            requisition.delivery_address.strip()
            if requisition.delivery_address else '',
        )
        res.update({
            'notes': '',
            'requesting_operating_unit_id': requisition.operating_unit_id.id,
            'delivery_address': combined_address,
            'payment_term_id': supplier.property_supplier_payment_term.id,
            'is_central_purchase': requisition.is_central_purchase,
        })
        # Case central purchase, use selected OU
        if self._context.get('sel_operating_unit_id', False):
            operating_unit_id = self._context.get('sel_operating_unit_id')
            picking_type_id = self._context.get('sel_picking_type_id')
            location_id = self._context.get('sel_location_id')
            res.update({
                'operating_unit_id': operating_unit_id,
                'picking_type_id': picking_type_id,
                'location_id': location_id,
            })
        return res

    @api.model
    def _prepare_purchase_order_line(self, requisition, requisition_line,
                                     purchase_id, supplier):
        res = super(PurchaseRequisition, self).\
            _prepare_purchase_order_line(requisition, requisition_line,
                                         purchase_id, supplier)
        # Always use price and tax_ids from pr_line (NOT from product)
        res.update({
            'name': requisition_line.product_name or res['name'],
            'price_unit': requisition_line.price_unit or res['price_unit'],
            'taxes_id': ([(6, 0, requisition_line.tax_ids.ids)] or
                         res['taxes_id']),
            'product_uom': (requisition_line.product_uom_id.id or
                            res['product_uom']),
            'fiscalyear_id': requisition_line.fiscalyear_id.id or False,
        })
        return res

    @api.multi
    def _check_product_type(self):
        self.ensure_one()
        if len(self.line_ids) == 0:
            raise ValidationError(
                _('Product line cannot be empty.')
            )
        for line in self.line_ids:
            if not line.product_id:
                raise ValidationError(
                    _("You have to specify products first.")
                )
        types = [(l.product_id.type in ('product', 'consu') and
                  'stock' or
                  l.product_id.type) for l in self.line_ids]
        if len(list(set(types))) > 1:
            raise ValidationError(
                _('All products must be of the same type')
            )
        return True

    @api.multi
    def to_verify(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        self._check_product_type()
        self.state = 'verify'
        return True

    @api.multi
    def rejected(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        # self.signal_workflow('rejected')
        self.state = 'rejected'

    @api.multi
    def send_pbweb_requisition(self):
        PWInterface = self.env['purchase.web.interface']
        PWInterface.send_pbweb_requisition(self)
        return True

    @api.multi
    def send_pbweb_requisition_cancel(self):
        if self.sent_pbweb:
            PWInterface = self.env['purchase.web.interface']
            PWInterface.send_pbweb_requisition_cancel(self)
        return True

    @api.multi
    def check_rfq_no(self):
        Order = self.env['purchase.order']
        rfqs = Order.search([('requisition_id', '=', self.id)])
        if self.purchase_method_id.require_rfq:
            if len(rfqs) == 0:
                raise ValidationError(
                    _("You haven't create the Request to Quotation yet.")
                )
            else:
                state_confirmed = 0
                for rfq in rfqs:
                    if rfq.state == 'confirmed':
                        state_confirmed += 1
                if state_confirmed == 0:
                    raise ValidationError(
                        _("At least one RfQ must be confirmed.")
                    )
        return True

    @api.multi
    def set_verification_info(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        pabiweb_active = self.env.user.company_id.pabiweb_active
        if pabiweb_active:  # If no connection to PRWeb, no need to send doc
            self.print_call_for_bid_form()
        self.write({
            'verify_uid': self._uid,
            'date_verify': fields.Date.context_today(self),
        })
        for order in self.purchase_ids:
            if order.state != 'cancel':
                order.write({
                    'verify_uid': self._uid,
                    'date_verify': fields.Date.context_today(self),
                })
        return True

    @api.multi
    def tender_in_progress(self):
        for requisition in self:
            requisition._check_product_type()
        res = super(PurchaseRequisition, self).tender_in_progress()
        return res

    @api.multi
    def tender_done(self, context=None):
        # ensure the tender to be done in PABIWeb confirmation.
        res = False
        for requisition in self:
            if requisition.state == 'open':
                res = super(PurchaseRequisition, self).\
                    tender_done()
                break
        return res

    @api.model
    def _purchase_request_cancel_message_content(self, pr, request):
        title = _('Cancel Call %s for your Request %s') % (
            pr.name, request.name)
        message = '<h3>%s</h3><ul>' % title
        message += _('The following requested items from Purchase Request %s '
                     'can be used to create new Call for Bids by cancelling '
                     'Purchase Bid %s.</ul>') % (request.name, pr.name)
        return message

    @api.multi
    def _purchase_request_cancel_message(self):
        request_obj = self.env['purchase.request']
        for pr in self:
            requests = []
            for line in pr.line_ids:
                for request_line in line.purchase_request_lines:
                    requests.append(request_line.request_id.id)
            for request_id in requests:
                request = request_obj.browse(request_id)
                request.state = 'approved'
                message = self._purchase_request_cancel_message_content(
                    pr, request)
                request.message_post(body=message)
        return True

    @api.model
    def get_doc_type(self):
        res = False
        WMethod = self.env['prweb.purchase.method']
        web_method = WMethod.search([
            ('type_id', '=', self.purchase_type_id.id),
            ('method_id', '=', self.purchase_method_id.id),
        ])
        for method in web_method:
            res = method.doctype_id
            break
        return res

    @api.multi
    def tender_cancel(self):
        res = super(PurchaseRequisition, self).tender_cancel()
        self._purchase_request_cancel_message()
        return res

    @api.multi
    def wkf_validate_vs_quotation(self):
        """ Case Central Purchase, quotation amount should not exceed """
        decimal_prec = self.env['decimal.precision']
        precision = decimal_prec.precision_get('Account')
        for requisition in self:
            if not requisition.is_central_purchase:
                continue
            total = sum([o.amount_total for o in requisition.purchase_ids])
            if float_compare(total, requisition.amount_total,
                             precision) == 1:
                raise ValidationError(
                    _('Total quotation amount exceed Call for Bid amount')
                )
        return True

    @api.multi
    def print_call_for_bid_form(self):
        Attachment = self.env['ir.attachment']
        self.ensure_one()
        doc_type = self.get_doc_type()
        if not doc_type:
            raise ValidationError(_("Can't get PD Document Type."))
        Report = self.env['ir.actions.report.xml']
        matching_reports = Report.search([
            ('model', '=', self._name),
            ('report_type', '=', 'pdf'),
            ('report_name', '=',
             'purchase.requisition_' + doc_type.name.lower())],)
        if matching_reports:
            report = matching_reports[0]
            result, _x = openerp.report.render_report(self._cr, self._uid,
                                                      [self.id],
                                                      report.report_name,
                                                      {'model': self._name})
            eval_context = {'time': time, 'object': self}
            if not report.attachment or not eval(report.attachment,
                                                 eval_context):
                # no auto-saving of report as attachment, need to do manually
                exist_pd_file = Attachment.search([
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'purchase.requisition'),
                    ('name', 'ilike', '_main_form.pdf'),
                ])
                if len(exist_pd_file) > 0:
                    exist_pd_file.unlink()
                result = base64.b64encode(result)
                file_name = self.display_name
                file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
                file_name += "_main_form.pdf"
                Attachment.create({
                    'name': file_name,
                    'datas': result,
                    'datas_fname': file_name,
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary'
                })

    @api.multi
    def print_requisition_with_condition(self):
        self.ensure_one()
        doc_type = self.get_doc_type()
        if not doc_type:
            raise ValidationError(_("Can't get PD Document Type."))
        report_name = 'purchase.requisition_' + doc_type.name.lower()
        return self.env['report'].get_action(self, report_name)

    @api.multi
    def print_approval_report(self):
        self.ensure_one()
        report_name = 'purchase.requisition_summary'
        return self.env['report'].get_action(self, report_name)


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
    product_name = fields.Text(
        string='Description',
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        'Fiscal Year',
        readonly=True,
    )
    is_green_product = fields.Boolean(
        string='Green Product',
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


class PurchaseRequisitionCommittee(models.Model):
    _name = 'purchase.requisition.committee'
    _description = 'Purchase Requisition Committee'
    _order = 'sequence, id'

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
        required=True,
    )
    position = fields.Char(
        string='Position',
    )
    committee_type_id = fields.Many2one(
        'purchase.committee.type',
        string='Type',
    )
