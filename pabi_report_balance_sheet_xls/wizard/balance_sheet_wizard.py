# -*- coding: utf-8 -*-
from openerp import models, api


class BalanceSheetWizard(models.TransientModel):
    _inherit = 'accounting.report'

    @api.multi
    def xls_export(self):
        res = self.check_report()
        if self._context.get('xls_export', False):
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_balance_sheet_xls',
                'datas': res['data']
            }
        return res
