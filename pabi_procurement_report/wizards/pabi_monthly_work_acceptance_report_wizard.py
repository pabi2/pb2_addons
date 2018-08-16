# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiMonthlyWorkAcceptanceReportWizard(models.TransientModel, Common):

    _name = 'pabi.monthly.work.acceptance.report.wizard'

    # Search Criteria
    # operating_unit_id = fields.Many2many(
    #     'operating.unit.view',
    #     'monthly_work_acceptance_ou_view_rel'
    #     'work_acc_report_id', 'ou_id',
    #     string='Operating Unit',
    # )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
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
            'org_ids',
            'date_from',
            'date_to',
        ]
        report_name = 'xlsx_report_pabi_monthly_work_acceptance'
        return self._get_report(fields, report_name)
