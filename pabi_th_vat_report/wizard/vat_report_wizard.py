# -*- coding: utf-8 -*-

from openerp import fields, models, api


class AccountVatReport(models.TransientModel):
    _inherit = 'account.vat.report'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        required=True,
    )