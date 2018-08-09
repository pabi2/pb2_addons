# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiStockBalanceReportWizard(models.TransientModel, Common):

    _name = 'pabi.stock.balance.report.wizard'

    # Search Criteria
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True
    )

    @api.multi
    def xls_export(self):
        fields = [
            'tag_id',
        ]
        report_name = 'xlsx_report_pabi_stock_balance'
        return self._get_report(fields, report_name)
