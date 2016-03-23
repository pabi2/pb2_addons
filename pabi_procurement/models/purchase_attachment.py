# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PurchaseRequestAttachment(models.Model):
    _name = 'purchase.request.attachment'
    _description = 'Purchase Request Attachment'

    request_id = fields.Many2one(
        'purchase_request',
        'Purchase Request'
    )
    name = fields.Char(string='File Name')
    file_url = fields.Binary(string='File Url')


class PurchaseRequisitionAttachment(models.Model):
    _name = 'purchase.requisition.attachment'
    _description = 'Purchase Requisition Attachment'

    requisition_id = fields.Many2one(
        'purchase_requisition',
        'Purchase Requisition'
    )
    name = fields.Char(string='File Name')
    file_url = fields.Binary(string='File Url')
