# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiSlaBalanceReportWizard(models.TransientModel, Common):

    _name = 'pabi.monthly.sla.balance.report.wizard'

    # Search Criteria
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    select_status = fields.Selection(
        [
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ],
        string='Status',
    )

    @api.multi
    def xls_export(self):
        fields = [
            'operating_unit_id',
            'status',
        ]
        report_name = 'xlsx_report_pabi_sla_balance'
        return self._get_report(fields, report_name)
