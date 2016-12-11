# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountTaxReportWizard(models.TransientModel):
    _inherit = 'account.tax.report.wizard'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        required=True,
    )

    @api.multi
    def run_report(self):
        res = super(AccountTaxReportWizard, self).run_report()
        # Criterias
        taxbranch = self.taxbranch_id
        res['datas']['parameters']['taxbranch_id'] = taxbranch.id
        # Display
        res['datas']['parameters']['branch_name'] = taxbranch.name
        res['datas']['parameters']['branch_vat'] = taxbranch.taxid
        res['datas']['parameters']['branch_taxbranch'] = taxbranch.code
        res['datas']['parameters']['advance_sequence'] = True
        return res
