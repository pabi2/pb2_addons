# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    doc_ref = fields.Char(
        string='Doc Ref',
        copy=False,
    )
