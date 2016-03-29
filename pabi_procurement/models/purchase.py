# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    _RECEIVE_CON = [
        ('1', 'Day'),
        ('2', 'Date'),
    ]

    @api.depends('amount_total', 'fine_rate')
    @api.onchange('amount_total', 'fine_rate')
    def _compute_total_fine(self):
        self.total_fine = self.amount_total * self.fine_rate

    date_reference = fields.Date(
        'Reference Date',
        help="Date when the PO has been referenced",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        readonly=True,
        track_visibility='onchange',
    )
    mycontract_id = fields.Selection(
        selection=_CONTRACT,
        string='myContract',
        default='1',
    )
    receive_date_con = fields.Selection(
        selection=_RECEIVE_CON,
        string='Receive Date Condition',
        track_visibility='onchange',
        default='1',
    )
    picking_receive_date = fields.Date(
        ' ',
        help="Picking Receive Date",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    date_contract_start = fields.Date(
        'Contract Start Date',
        help="Date when the contract is started",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    date_contract_end = fields.Date(
        'Contract End Date',
        help="Date when the contract is ended",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        track_visibility='onchange',
    )
    fine_rate = fields.Float(
        'Fine Rate',
        _compute='_compute_total_fine',
        store=True,
        default=0.0,
    )
    total_fine = fields.Float(
        'Total Fine',
        _compute='_compute_total_fine',
        store=True,
    )
    committee_ids = fields.One2many(
        'purchase.order.committee', 'order_id',
        'Committee',
        readonly=False,
    )
    create_by = fields.Many2one(
        'res.users',
        'Create By',
    )
    verified_by = fields.Many2one(
        'res.users',
        'Verified By',
    )
    approved_by = fields.Many2one(
        'res.users',
        'Approved By',
    )
    position = fields.Char('Position')
    date_approval = fields.Date(
        'Approved Date',
        help="Date when the PO has been approved",
        default=lambda *args:
        time.strftime('%Y-%m-%d %H:%M:%S'),
        readonly=True,
        track_visibility='onchange',
    )


class PurchaseType(models.Model):
    _name = 'purchase.type'
    _description = 'PABI2 Purchase Type'

    name = fields.Char(string='Purchase Type')


class PurchaseMethod(models.Model):
    _name = 'purchase.method'
    _description = 'PABI2 Purchase Method'

    name = fields.Char(string='Purchase Method')
