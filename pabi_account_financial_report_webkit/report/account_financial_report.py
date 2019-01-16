# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.addons.account.report.account_financial_report import \
    report_account_common


class report_account_common(report_account_common):

    # Overwrite old method
    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        ids2 = self.pool.get('account.financial.report') \
            ._get_children_by_order(
                self.cr, self.uid, [data['form']['account_report_id'][0]],
                context=data['form']['used_context'])
        for report in self.pool.get('account.financial.report').browse(
                self.cr, self.uid, ids2, context=data['form']['used_context']):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and
                        report.style_overwrite or report.level,
                'account_type': report.type == 'sum' and 'view' or False,
                # used to underline the financial report balances
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = \
                    self.pool.get('account.financial.report').browse(
                        self.cr, self.uid, report.id,
                        context=data['form']['comparison_context']).balance * \
                    report.sign or 0.0
            lines.append(vals)

            ctx = {}
            if 'active_test' in data['form']['used_context']:
                ctx['active_test'] = \
                    data['form']['used_context']['active_test']

            account_ids = []
            if report.display_detail == 'no_detail':
                # the rest of the loop is used to display the details of the
                # financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(
                    self.cr, self.uid, [x.id for x in report.account_ids],
                    context=ctx)
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(
                    self.cr, self.uid,
                    [('user_type', 'in',
                      [x.id for x in report.account_type_ids])], context=ctx)
            if account_ids:
                for account in account_obj.browse(
                        self.cr, self.uid, account_ids,
                        context=data['form']['used_context']):
                    # if there are accounts to display, we add them to the
                    # lines with a level equals to their level in
                    # the COA + 1 (to avoid having them with a too low level
                    # that would conflicts with the level of data
                    # financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and \
                       account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance': account.balance != 0 and
                        account.balance * report.sign or account.balance,
                        'type': 'account',
                        'level':
                            report.display_detail == 'detail_with_hierarchy'
                            and min(account.level + 1, 6) or 6,
                            # account.level + 1
                        'account_type': account.type,
                    }

                    if data['form']['debit_credit']:
                        vals['debit'] = account.debit
                        vals['credit'] = account.credit
                    if not currency_obj.is_zero(
                       self.cr, self.uid, account.company_id.currency_id,
                       vals['balance']):
                        flag = True
                    if data['form']['enable_filter']:
                        vals['balance_cmp'] = account_obj.browse(
                            self.cr, self.uid, account.id,
                            context=data['form']['comparison_context']) \
                                .balance * report.sign or 0.0
                        if not currency_obj.is_zero(
                           self.cr, self.uid, account.company_id.currency_id,
                           vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines


class report_financial(osv.AbstractModel):
    _inherit = 'report.account.report_financial'
    _wrapped_report_class = report_account_common
