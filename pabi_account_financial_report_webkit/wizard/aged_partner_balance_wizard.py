# -*- coding: utf-8 -*-
from datetime import date
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class AccountAgedTrialBalance(orm.TransientModel):
    """Will launch age partner balance report.
    This report is based on Open Invoice Report
    and share a lot of knowledge with him
    """

    _inherit = "open.invoices.webkit"
    _name = "account.aged.trial.balance.webkit"
    _description = "Aged partner balanced"

    def _get_current_fiscalyear(self, cr, uid, context=None):
        user_obj = self.pool['res.users']
        company = user_obj.browse(cr, uid, uid, context=context).company_id
        fyear_obj = self.pool['account.period']
        today = date.today().strftime(DATE_FORMAT)
        fyear_ids = fyear_obj.search(
            cr, uid,
            [('date_start', '>=', today),
             ('date_stop', '<=', today),
             ('company_id', '=', company.id)],
            limit=1,
            context=context)
        if fyear_ids:
            return fyear_ids[0]

    _columns = {
        'filter': fields.selection(
            [('filter_period', 'Periods')],
            "Filter by",
            required=True),
        'fiscalyear_id': fields.many2one(
            'account.fiscalyear',
            'Fiscal Year',
            required=True),
        'period_to': fields.many2one('account.period', 'End Period',
                                     required=True),
    }

    _defaults = {
        'filter': 'filter_period',
        'fiscalyear_id': _get_current_fiscalyear,
    }

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear=False,
                            period_id=False, date_to=False, until_date=False,
                            context=None):
        res = super(AccountAgedTrialBalance, self).onchange_fiscalyear(
            cr, uid, ids, fiscalyear=fiscalyear, period_id=period_id,
            date_to=date_to, until_date=until_date, context=context
        )
        filters = self.onchange_filter(cr, uid, ids, filter='filter_period',
                                       fiscalyear_id=fiscalyear,
                                       context=context)
        res['value'].update({
            'period_from': filters['value']['period_from'],
            'period_to': filters['value']['period_to'],
        })
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        # we update form with display account value
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_aged_trial_balance_webkit',
                'datas': data}
