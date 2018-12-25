# -*- coding: utf-8 -*-
from openerp.osv import orm


class AccountTrialBalanceWizard(orm.TransientModel):
    """Will launch trial balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "trial.balance.webkit"
    _description = "Trial Balance Report"

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountTrialBalanceWizard, self).\
            pre_print_report(cr, uid, ids, data, context)

        # PABI2
        data['specific_report'] = True

        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        context = context or {}
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)

        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_trial_balance_webkit',
                'datas': data}
