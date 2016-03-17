# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProcurementAttachment(models.Model):
    _name = 'procurement.attachment'
    _description = 'Procurement Attachment'

    pr_id = fields.Many2one('purchase_request', 'Purchase Request')
    name = fields.Char(string='File Name')
    file_url = fields.Binary(string='File Url')
