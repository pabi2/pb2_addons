# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiSupplierEvaluationReportWizard(models.TransientModel, Common):

    _name = 'pabi.supplier.evaluation.report.wizard'

    # Search Criteria
    partner_id = fields.Many2one(
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
            'partner_id', 'org_ids'
        ]
        report_name = 'xlsx_report_pabi_supplier_evaluation'
        return self._get_report(fields, report_name)
