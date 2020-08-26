# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    is_import = fields.Boolean(
        string='Imported', readonly=True
    )
