# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiSlaBalanceReportWizard(models.TransientModel, Common):

    _name = 'pabi.monthly.sla.balance.report.wizard'

    # Search Criteria
    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    date_end = fields.Date(
        string='Date End',
        required=True
    )

    @api.multi
    def xls_export(self):
        fields = [
            'org_ids',
            'date_end',
        ]
        report_name = 'xlsx_report_pabi_sla_balance'
        return self._get_report(fields, report_name)
