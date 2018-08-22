# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiGreenProductSummaryReportWizard(models.TransientModel, Common):

    _name = 'pabi.green.product.summary.report.wizard'

    # Search Criteria
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )

    @api.multi
    def xls_export(self):
        fields = [
            'org_ids',
            'partner_ids',
        ]
        report_name = 'xlsx_report_pabi_green_product_summary'
        return self._get_report(fields, report_name)
