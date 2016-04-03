# -*- coding: utf-8 -*-

from openerp import fields, models, api
import time


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    _CONTRACT = [
        ('1', 'from myContract'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]

    _RECEIVE_DATE_CONDITION = [
        ('day', 'Day'),
        ('date', 'Date'),
    ]

    date_reference = fields.Date(
        string='Reference Date',
        default=fields.Date.today(),
        readonly=True,
        track_visibility='onchange',
    )
    mycontract_id = fields.Selection(
        selection=_CONTRACT,
        string='myContract',
        default='1',
    )
    receive_date_condition = fields.Selection(
        selection=_RECEIVE_DATE_CONDITION,
        string='Receive Date Condition',
        track_visibility='onchange',
        default='day',
    )
    picking_receive_date = fields.Date(
        string='Picking Receive Date',
        default=fields.Date.today(),
        track_visibility='onchange',
    )
    date_contract_start = fields.Date(
        string='Contract Start Date',
        default=fields.Date.today(),
        track_visibility='onchange',
    )
    date_contract_end = fields.Date(
        string='Contract End Date',
        help="Date when the contract is ended",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    fine_rate = fields.Float(
        string='Fine Rate',
        default=0.0,
    )
    total_fine = fields.Float(
        string='Total Fine',
        compute='_compute_total_fine',
        store=True,
    )
    committee_ids = fields.One2many(
        'purchase.order.committee',
        'order_id',
        string='Committee',
        readonly=False,
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

    @api.one
    @api.depends('amount_total', 'fine_rate')
    def _compute_total_fine(self):
        self.total_fine = self.amount_total * self.fine_rate

    @api.model
    def by_pass_approve(self, ids):
        po_rec = self.browse(ids)
        po_rec.action_button_convert_to_order()
        if po_rec.state != 'done':
            po_rec.state = 'done'
        return True


class PurchaseType(models.Model):
    _name = 'purchase.type'
    _description = 'PABI2 Purchase Type'

    name = fields.Char(
        string='Purchase Type',
    )


class PurchaseMethod(models.Model):
    _name = 'purchase.method'
    _description = 'PABI2 Purchase Method'

    name = fields.Char(
        string='Purchase Method',
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
    responsible = fields.Char(
        string='Responsible',
    )
    committee_type = fields.Char(
        string='Type',
    )
    order_id = fields.Many2one(
        'purchase_order',
        string='Purchase Order',
    )
