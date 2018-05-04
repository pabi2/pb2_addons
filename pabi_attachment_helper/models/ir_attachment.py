# -*- coding: utf-8 -*-
from openerp import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    res_id = fields.Integer(
        readonly=False,
    )
    attach_by = fields.Many2one(
        'res.users',
        string="Attach By",
        default=lambda self: self.env.user,
    )
