# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountTaxReport(models.Model):
    _inherit = 'account.tax.report'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
    )

    def _select(self):
        res = super(AccountTaxReport, self)._select()
        res += ', taxbranch_id'
        return res
