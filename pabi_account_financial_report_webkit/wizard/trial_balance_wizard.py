# -*- coding: utf-8 -*-
from openerp.osv import orm
from lxml import etree


class AccountTrialBalanceWizard(orm.TransientModel):
    """Will launch trial balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "trial.balance.webkit"
    _description = "Trial Balance Report"

    def _print_report(self, cursor, uid, ids, data, context=None):
        context = context or {}
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)

        # PABI2
        data['specific_report'] = True

        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_trial_balance_webkit',
                'datas': data}

    # PABI2
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(AccountTrialBalanceWizard, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = []
        for index in range(self.COMPARISON_LEVEL):
            nodes += \
                doc.xpath("//field[@name='comp%s_period_from']" % (index, ))
            nodes += \
                doc.xpath("//field[@name='comp%s_period_to']" % (index, ))
        for node in nodes:
            node.set('domain', "[(1, '=', 1)]")
        res['arch'] = etree.tostring(doc)
        return res

    def onchange_filter(self, cr, uid, ids, filter='filter_no',
                        fiscalyear_id=False, context=None):
        res = {}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f
                                   ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               /*AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_start ASC*/
                               ORDER BY p.code ASC /*PABI2*/
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f
                                   ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               /*AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_stop DESC*/
                               ORDER BY p.code DESC /*PABI2*/
                               LIMIT 1) AS period_stop''',
                       (fiscalyear_id, fiscalyear_id))
            periods = [i[0] for i in cr.fetchall()]
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to':
                            end_period, 'date_from': False, 'date_to': False}
            return res
        return super(AccountTrialBalanceWizard, self).onchange_filter(
            cr, uid, ids, filter=filter, fiscalyear_id=fiscalyear_id,
            context=context)

    def onchange_comp_filter(self, cr, uid, ids, index,
                             main_filter='filter_no', comp_filter='filter_no',
                             fiscalyear_id=False, start_date=False,
                             stop_date=False, context=None):
        res = {}
        fy_obj = self.pool.get('account.fiscalyear')
        last_fiscalyear_id = False
        if fiscalyear_id:
            fiscalyear = fy_obj.browse(cr, uid, fiscalyear_id, context=context)
            last_fiscalyear_ids = fy_obj.search(
                cr, uid, [('date_stop', '<', fiscalyear.date_start)],
                limit=self.COMPARISON_LEVEL, order='date_start desc',
                context=context)
            if last_fiscalyear_ids:
                if len(last_fiscalyear_ids) > index:
                    # first element for the comparison 1, second element for
                    # the comparison 2
                    last_fiscalyear_id = last_fiscalyear_ids[index]

        fy_id_field = "comp%s_fiscalyear_id" % (index,)
        period_from_field = "comp%s_period_from" % (index,)
        period_to_field = "comp%s_period_to" % (index,)
        date_from_field = "comp%s_date_from" % (index,)
        date_to_field = "comp%s_date_to" % (index,)
        if comp_filter == 'filter_period' and last_fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f
                                   ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %(fiscalyear)s
                               /*AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_start ASC*/
                               ORDER BY p.code ASC /*PABI2*/
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f
                                   ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %(fiscalyear)s
                               AND p.date_start < NOW()
                               /*AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_stop DESC*/
                               ORDER BY p.code DESC /*PABI2*/
                               LIMIT 1) AS period_stop''',
                       {'fiscalyear': last_fiscalyear_id})
            periods = [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {fy_id_field: False,
                            period_from_field: start_period,
                            period_to_field: end_period,
                            date_from_field: False,
                            date_to_field: False}
            return res
        return super(AccountTrialBalanceWizard, self).onchange_comp_filter(
            cr, uid, ids, index, main_filter=main_filter,
            comp_filter=comp_filter, fiscalyear_id=fiscalyear_id,
            start_date=start_date, stop_date=stop_date, context=context)
