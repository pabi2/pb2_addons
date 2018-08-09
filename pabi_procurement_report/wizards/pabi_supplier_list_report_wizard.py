# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiSupplierListReportWizard(models.TransientModel, Common):

    _name = 'pabi.supplier.list.report.wizard'

    # Search Criteria
    tag_id = fields.Many2one(
        'res.partner.tag',
        string='Tag',
    )

    @api.multi
    def xls_export(self):
        fields = [
            'tag_id',
        ]
        report_name = 'xlsx_report_pabi_supplier_list'
        return self._get_report(fields, report_name)
