# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiComparisonPrPoReportWizard(models.TransientModel, Common):

    _name = 'pabi.comparison.pr.po.report.wizard'

    # Search Criteria
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )

    @api.multi
    def xls_export(self):
        fields = [
            'partner_id',
        ]
        report_name = 'xlsx_report_pabi_comparison_pr_po'
        return self._get_report(fields, report_name)
