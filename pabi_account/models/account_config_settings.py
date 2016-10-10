# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    tax_move_by_taxbranch = fields.Boolean(
        string="Tax Account Move by Tax Branch",
        related='company_id.tax_move_by_taxbranch',
    )
    wht_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string="Taxbranch for Withholding Tax",
        related='company_id.wht_taxbranch_id',
    )
