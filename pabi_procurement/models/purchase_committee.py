# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PurchaseRequestCommittee(models.Model):
    _name = 'purchase.request.committee'
    _description = 'Purchase Request Committee'

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
    request_id = fields.Many2one(
        'purchase_request',
        string='Purchase Request',
    )


class PurchaseRequisitionCommittee(models.Model):
    _name = 'purchase.requisition.committee'
    _description = 'Purchase Requisition Committee'

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
    requisition_id = fields.Many2one(
        'purchase_requisition',
        string='Purchase Requisition',
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
