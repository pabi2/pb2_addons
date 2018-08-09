# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiMonthlyWorkAcceptanceReportWizard(models.TransientModel, Common):

    _name = 'pabi.monthly.work.acceptance.report.wizard'

    # Search Criteria
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    date_from = fields.Date(
        string='Date From',
    )
    date_to = fields.Date(
        string='Date To',
    )

    @api.multi
    def xls_export(self):
        fields = [
            'operating_unit_id',
            'date_from',
            'date_to',
        ]
        report_name = 'xlsx_report_pabi_monthly_work_acceptance'
        return self._get_report(fields, report_name)
