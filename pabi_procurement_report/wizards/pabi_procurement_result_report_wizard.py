# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiProcurementResultReportWizard(models.TransientModel, Common):

    _name = 'pabi.procurement.result.report.wizard'

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
            'partner_ids',
            'org_ids',
        ]
        report_name = 'xlsx_report_pabi_procurement_result_list'
        return self._get_report(fields, report_name)
