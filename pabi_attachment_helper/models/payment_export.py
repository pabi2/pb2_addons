# -*- coding: utf-8 -*-
from openerp import models, fields


class PaymentExport(models.Model):
    _inherit = 'payment.export'

    attachment_ids = fields.One2many(
        'ir.attachment',
        'payment_export_id',
        string='Attachment',
        copy=False,
    )
