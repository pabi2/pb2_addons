# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProcurementCommittee(models.Model):
    _name = 'procurement.committee'
    _description = 'Procurement Committee'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name')
    position = fields.Char(string='Position')
    responsible = fields.Char(string='Responsible')
    pr_id = fields.Many2one('purchase_request', 'Purchase Request')
    po_id = fields.Many2one('purchase_order', 'Purchase Order')
