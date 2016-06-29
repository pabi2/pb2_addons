# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError
from openerp.tools import float_compare
from openerp.osv.orm import browse_record_list, browse_record, browse_null


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

    @api.model
    def by_pass_approve(self, ids):
        quotation = self.browse(ids)
        quotation.action_button_convert_to_order()
        if quotation.state != 'done':
            quotation.state = 'done'
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
        # self.wkf_validate_vs_requisition()
        return super(PurchaseOrder, self).action_button_convert_to_order()

    @api.multi
    def action_picking_create(self):
        res = super(PurchaseOrder, self).action_picking_create()
        picking = self.env['stock.picking'].search([('id', '=', res[0])])
        picking.verified = True
        return res

    @api.multi
    def action_force_done(self):
        Picking = self.env['stock.picking']
        for order in self:
            picking = Picking.search([
                ('state', 'not in', ('done', 'cancel')),
                '|',
                ('origin', '=', order.name),
                ('group_id', '=', order.name),
            ])
            if len(picking) > 0:
                picking.action_cancel()
        self.wkf_po_done()
        return True

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
                    'mycontract_id': porder.mycontract_id,
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
    web_method_ids = fields.Many2many(
        string='PRWeb Method',
        comodel_name='prweb.purchase.method',
        relation='prweb_purchase_method_rel',
        column1='committee_type_id',
        column2='method_id',
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
