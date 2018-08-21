# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiPurchaseAnnualReportWizard(models.TransientModel, Common):

    _name = 'pabi.purchase.annual.report.wizard'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )

    @api.multi
    def xls_export(self):
        fields = [
            'org_ids',
        ]
        report_name = 'xlsx_report_pabi_purchase_annual'
        return self._get_report(fields, report_name)
