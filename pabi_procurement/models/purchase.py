# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import time


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    _CONTRACT = {
        ('1', 'from myContract'),
        ('2', '4'),
        ('3', '3'),
        ('4', '4'),
    }

    _RECEIVE_CON = {
        ('1', 'จำนวนวัน'),
        ('2', 'วันที่'),
    }

    @api.depends('amount_total', 'fine_rate')
    @api.onchange('amount_total', 'fine_rate')
    def _compute_total_fine(self):
        self.total_fine = self.amount_total * self.fine_rate

    date_reference = fields.Date('Reference Date',
                                 help="Date when the PO has been referenced",
                                 default=lambda *args:
                                 time.strftime('%Y-%m-%d %H:%M:%S'),
                                 readonly=True,
                                 track_visibility='onchange')

    mycontract_id = fields.Selection(selection=_CONTRACT,
                                     track_visibility='onchange',
                                     default='1')

    receive_date_con = fields.Selection(selection=_RECEIVE_CON,
                                        string='Receive Date Condition',
                                        track_visibility='onchange',
                                        default='1')

    receive_date_date = fields.Date(' ',
                                    help="Pick Receive Date",
                                    default=lambda *args:
                                    time.strftime('%Y-%m-%d %H:%M:%S'),
                                    track_visibility='onchange')

    date_contract_start = fields.Date('Contract Start Date',
                                      help="Date when the contract is started",
                                      default=lambda *args:
                                      time.strftime('%Y-%m-%d %H:%M:%S'),
                                      track_visibility='onchange')

    date_contract_end = fields.Date('Contract End Date',
                                    help="Date when the contract is ended",
                                    default=lambda *args:
                                    time.strftime('%Y-%m-%d %H:%M:%S'),
                                    track_visibility='onchange')

    fine_rate = fields.Float('Fine Rate',
                             _compute='_compute_total_fine',
                             store=True,
                             default=0)

    total_fine = fields.Float('Total Fine',
                              _compute='_compute_total_fine',
                              store=True,
                              )

    committee_ids = fields.One2many('procurement.committee', 'po_id',
                                    'PO Committee',
                                    readonly=False,
                                    track_visibility='onchange')
