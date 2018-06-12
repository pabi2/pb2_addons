# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .procurement_common_report_wizard import Common


class PabiPurchaseSummarizeReportWizard(models.TransientModel, Common):

    _name = 'pabi.purchase.summarize.report.wizard'

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    @api.multi
    def xls_export(self):
        fields = ['date_from', 'date_to']
        report_name = 'xlsx_report_pabi_purchase_summarize'
        return self._get_report(fields, report_name)
