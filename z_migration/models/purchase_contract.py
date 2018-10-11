# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseContract(models.Model):
    _inherit = 'purchase.contract'

    poc_code = fields.Char(
        readonly=False,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Last Updated By',
        readonly=False,
    )
