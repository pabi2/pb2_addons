# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare
from openerp.osv.orm import browse_record_list, browse_record, browse_null


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('confirmed', 'Waiting to Release'),
        ('approved', 'PO Released'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    state = fields.Selection(
        STATE_SELECTION,
    )
    dummy_quote_id = fields.Many2one(
        'purchase.order',
        string='Quotation Reference',
        compute='_compute_dummy_quote_id',
    )
    date_reference = fields.Date(
        string='Reference Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    contract_id = fields.Many2one(
        'purchase.contract',
        string='Contract',
        compute='_compute_contract_id',
        store=True
    )
    date_contract_start = fields.Date(
        string='Contract Start Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)]},
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
    doc_approve_position_id = fields.Many2one(
        'hr.position',
        string='Position',
        compute="_compute_doc_approve_position_id",
    )
    order_state = fields.Selection(
        string='PO Status',
        related='order_id.state',
        readonly=True,
    )
    delivery_address = fields.Text(
        string='Delivery Address',
    )
    is_central_purchase = fields.Boolean(
        string='Central Purchase',
        readonly=True,
        default=False,
    )
    select_reason = fields.Many2one(
        'purchase.select.reason',
        string='Selected Reason',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    shipment_count = fields.Integer(
        string='Incoming Shipments',
        compute='_compute_shipment_count',
    )

    @api.multi
    def _compute_shipment_count(self):
        Group = self.env['procurement.group']
        Picking = self.env['stock.picking']
        for rec in self:
            # Shipment
            groups = Group.search([('name', '=', rec.name)])
            pickings = Picking.search([('group_id', 'in', groups.ids)])
            rec.shipment_count = len(pickings)

    @api.multi
    def view_picking(self):
        """ Change po.picking_ids to picking with same procurement group """
        self.ensure_one()
        action = super(PurchaseOrder, self).view_picking()
        action.update({'domain': False, 'views': False, 'res_id': False})
        Group = self.env['procurement.group']
        Picking = self.env['stock.picking']
        Data = self.env['ir.model.data']

        groups = Group.search([('name', '=', self.name)])
        pickings = Picking.search([('group_id', 'in', groups.ids)])

        if len(pickings) > 1:
            action['domain'] = [('id', '=', pickings.ids)]
        else:
            res = Data.get_object_reference('stock', 'view_picking_form')
            action['views'] = [(res and res[1] or False, 'form')]
            action['res_id'] = pickings.ids and pickings.ids[0] or False
        return action

    @api.multi
    def name_get(self):
        result = []
        for po in self:
            if po.contract_id:
                result.append((po.id, '%s (%s)' %
                              (po.name, po.contract_id.display_code)))
            else:
                result.append((po.id, po.name))
        return result

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
            committee_line = self._prepare_committee_line(line, order_id)
            committees.append([0, False, committee_line])
        return committees

    @api.multi
    @api.depends('doc_approve_uid')
    def _compute_doc_approve_position_id(self):
        for rec in self:
            Employee = self.env['hr.employee']
            employee = Employee.search([('user_id', '=',
                                         rec.doc_approve_uid.id)])
            for emp in employee:
                rec.doc_approve_position_id = emp.position_id

    @api.one
    def _compute_dummy_quote_id(self):
        self.dummy_quote_id = self.id

    @api.multi
    @api.depends('requisition_id.contract_ids.state')
    def _compute_contract_id(self):
        # As discuss w/ Sunchai, let's use newest contract, regardless of state
        for rec in self:
            if rec.requisition_id and rec.requisition_id.contract_ids:
                latest_contract_id = max(rec.requisition_id.contract_ids.ids)
                rec.contract_id = latest_contract_id

    @api.model
    def check_over_requisition_limit(self):
        if self.state not in ('done', 'cancel'):
            po_total_payment = 0
            confirmed_rfqs = self.search(
                [
                    ('requisition_id', '=', self.requisition_id.id),
                    ('state', '=', 'done'),
                ]
            )
            for rfq in confirmed_rfqs:
                po_total_payment += rfq.amount_total
            over_rate = (self.requisition_id.amount_total * 10) / 100
            cfb_total_amount = self.requisition_id.amount_total + over_rate
            if po_total_payment + self.amount_total > cfb_total_amount:
                raise ValidationError(
                    _("""Can't evaluate this acceptance.
                         This RfQ total amount is over than
                         call for bids total amount.""")
                )
        return True

    @api.model
    def _check_request_for_quotation(self):
        if self.requisition_id.purchase_method_id.require_rfq:
            raise ValidationError(
                _("Can't convert to order. Have to wait for PD approval.")
            )
        self.check_over_requisition_limit()
        return True

    @api.model
    def by_pass_approve(self, ids):
        quotation = self.browse(ids)
        quotation._check_request_for_quotation()
        quotation.action_button_convert_to_order()
        if quotation.state != 'done':
            quotation.state = 'done'
        return True

    @api.multi
    def wkf_confirm_order(self):
        for order in self:
            if order.requisition_id.is_central_purchase:
                order.requisition_id.exclusive = 'multiple'
                order.requisition_id.multiple_rfq_per_supplier = True
            order.check_over_requisition_limit()
            res = super(PurchaseOrder, order).wkf_confirm_order()
            return res

    @api.multi
    def wkf_action_cancel(self):
        res = super(PurchaseOrder, self).wkf_action_cancel()
        for order in self:
            self.state2 = 'cancel'
            if order.quote_id:
                order.quote_id.wkf_action_cancel()
                order.quote_id.state2 = 'cancel'
        return res

    @api.model
    def by_pass_cancel(self, ids):
        quotation = self.browse(ids)
        quotation.action_cancel()
        if quotation.state != 'cancel':
            quotation.state = 'cancel'
        return True

    @api.model
    def by_pass_delete(self, ids):
        quotation = self.browse(ids)
        for quote in quotation:
            quote.unlink()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.multi
    def wkf_validate_invoice_method(self):
        """ Change invoice method to 'or' when picking + service """
        for po in self:
            if po.invoice_method == 'picking' and \
                not any([l.product_id and
                         l.product_id.type in ('product', 'consu') and
                         l.state != 'cancel' for l in po.order_line]):
                po.invoice_method = 'manual'
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
                    raise ValidationError(
                        _('Confirmed amount exceed Call for Bid amount')
                    )
        return True

    @api.multi
    def action_button_convert_to_order(self):
        # Find doc type
        doctype = self.env['res.doctype'].get_doctype('purchase_order')
        fiscalyear_id = self.env['account.fiscalyear'].find()
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        res = super(PurchaseOrder, self).action_button_convert_to_order()
        orders = self.browse(res['res_id'])
        for order in orders:
            order.write({
                'origin': order.quote_id.origin,
                'committee_ids': self._prepare_order_committees(order.id),
                'requisition_id': order.quote_id.requisition_id.id,
            })
        return res

    @api.multi
    def action_picking_create(self):
        res = super(PurchaseOrder, self).action_picking_create()
        picking = self.env['stock.picking'].search([('id', '=', res[0])])
        picking.verified = True
        return res

    @api.v7
    def do_merge(self, cr, uid, ids, context=None):
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, browse_record_list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        context = dict(context or {})

        # Compute what the new orders should contain
        new_orders = {}

        order_lines_to_move = {}
        for porder in [
            order for order in self.browse(cr, uid, ids, context=context)
                if order.state == 'draft']:
            order_key = make_key(
                porder, (
                    'partner_id',
                    'location_id',
                    'pricelist_id',
                    'currency_id'
                )
            )
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            order_lines_to_move.setdefault(order_key, [])

            if not order_infos:
                requesting_ou = porder.requesting_operating_unit_id.id
                ou = porder.operating_unit_id.id
                doc_position = porder.doc_approve_position_id.id
                order_infos.update({
                    'order_type': 'purchase_order',
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'picking_type_id': porder.picking_type_id.id,
                    'requesting_operating_unit_id': requesting_ou,
                    'operating_unit_id': ou,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'currency_id': porder.currency_id.id,
                    'minimum_planned_date': porder.minimum_planned_date,
                    'verify_uid': porder.verify_uid.id,
                    'date_verify': porder.date_verify,
                    'doc_approve_position_id': doc_position,
                    'doc_approve_uid': porder.doc_approve_uid.id,
                    'date_doc_approve': porder.date_doc_approve,
                    'payment_term_id': porder.payment_term_id.id,
                    'partner_ref': porder.partner_ref,
                    'date_reference': porder.date_reference,
                    'contract_id': porder.contract_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position.id or False,
                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    note = (order_infos['notes'] or '') \
                        + ('\n%s' % (porder.notes,))
                    order_infos['notes'] = note
                if porder.origin:
                    origin = (order_infos['origin'] or '') \
                        + ' ' + porder.origin
                    order_infos['origin'] = origin

            order_lines_to_move[order_key] += \
                [order_line.id for order_line in porder.order_line
                    if order_line.state != 'cancel']
        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(6, 0, order_lines_to_move[order_key])]
            order_data['committee_ids'] = [(6, 0, porder.committee_ids.ids)]

            # create the new order
            context.update({'mail_create_nolog': True})
            neworder_id = self.create(cr, uid, order_data)
            self.message_post(
                cr,
                uid,
                [neworder_id],
                body=_("RFQ created"),
                context=context
            )
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                self.redirect_workflow(cr, uid, [(old_id, neworder_id)])
                self.signal_workflow(cr, uid, [old_id], 'purchase_cancel')

        return orders_info


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.order_id.is_central_purchase:
                raise ValidationError(
                    _('Deletion of purchase order line is not allowed,\n'
                      'please discard changes!'))
        return super(PurchaseOrderLine, self).unlink()


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
    doctype_id = fields.Many2one(
        'wkf.config.doctype',
        string='Doc Type',
        domain=[('module', '=', 'purchase')],
    )
    price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Price Range',
    )
    condition_id = fields.Many2one(
        'purchase.condition',
        string='Condition',
    )

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id,
                        '%s - %s' % (rec.type_id.name, rec.method_id.name)))
        return res


class PurchaseType(models.Model):
    _name = 'purchase.type'
    _description = 'PABI2 Purchase Type'

    name = fields.Char(
        string='Purchase Type',
        required=True,
    )


class PurchaseSelectReason(models.Model):
    _name = 'purchase.select.reason'
    _description = 'PABI2 Purchase Selected Reason'

    name = fields.Char(
        string='Select Reason',
        required=True,
    )


class PurchaseMethod(models.Model):
    _name = 'purchase.method'
    _description = 'PABI2 Purchase Method'

    name = fields.Char(
        string='Purchase Method',
        required=True,
    )
    require_rfq = fields.Boolean(
        string='Require for RfQ',
        help='At least 1 RfQ must be created before verifying CfBs',
    )


class PurchaseCommitteeType(models.Model):
    _name = 'purchase.committee.type'
    _description = 'PABI2 Purchase Committee Type'

    name = fields.Char(
        string='Purchase Committee Type',
        required=True,
    )
    code = fields.Char(
        string='Purchase Committee Type Code',
        required=False,
    )
    web_method_ids = fields.One2many(
        'purchase.committee.type.prweb.method',
        'committee_type_id',
        string='PR Methods',
    )
    # web_method_ids = fields.Many2many(
    #     string='PRWeb Method',
    #     comodel_name='prweb.purchase.method',
    #     relation='prweb_purchase_method_rel',
    #     column1='committee_type_id',
    #     column2='method_id',
    # )


class PurchaseCommiteeTypePRWebMethod(models.Model):
    _name = 'purchase.committee.type.prweb.method'
    _description = 'PABI2 Purchase Committee Type PR Web Method'
    _order = 'sequence, id'

    committee_type_id = fields.Many2one(
        'purchase.committee.type',
        string='Commitee Type',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    method_id = fields.Many2one(
        'prweb.purchase.method',
        string='PRWeb Method',
        required=True,
    )
    doctype_id = fields.Many2one(
        'wkf.config.doctype',
        string='Type',
        related='method_id.doctype_id',
        readonly=True,
    )
    price_range_id = fields.Many2one(
        'purchase.price.range',
        string='Price Range',
        related='method_id.price_range_id',
        readonly=True,
    )
    condition_id = fields.Many2one(
        'purchase.condition',
        string='Condition',
        related='method_id.condition_id',
        readonly=True,
    )


class PurchasePriceRange(models.Model):
    _name = 'purchase.price.range'
    _description = 'PABI2 Price Range'

    name = fields.Char(
        string='Purchase Price Range',
        required=True,
    )
    price_from = fields.Float(
        string='Price From',
        default=0.0,
    )
    price_to = fields.Float(
        string='Price To',
        default=0.0,
    )


class PurchaseCondition(models.Model):
    _name = 'purchase.condition'
    _description = 'PABI2 Purchase Condition'

    name = fields.Char(
        string='Purchase Condition',
        required=True,
    )
    condition_detail_ids = fields.Many2many(
        string='Purchase Condition Detail',
        comodel_name='purchase.condition.detail',
        relation='purchase_condition_rel',
        column1='condition_id',
        column2='condition_detail_id',
    )


class PurchaseConditionDetail(models.Model):
    _name = 'purchase.condition.detail'
    _description = 'PABI2 Purchase Condition Detail'

    name = fields.Char(
        string='Purchase Condition Detail',
        required=True,
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
        required=True,
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
        index=True,
        ondelete='cascade',
    )
