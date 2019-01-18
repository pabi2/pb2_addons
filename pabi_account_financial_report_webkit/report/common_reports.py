# -*- coding: utf-8 -*-
# TODO refactor helper in order to act more like mixin
# By using properties we will have a more simple signature in fuctions

import logging

from openerp.osv import osv
from openerp.tools.translate import _
from openerp.addons.account.report.common_report_header \
    import common_report_header

_logger = logging.getLogger('financial.reports.webkit')

MAX_MONSTER_SLICE = 50000


class CommonReportHeaderWebkit(common_report_header):

    """Define common helper for financial report"""

    ######################################################################
    # From getter helper                                                 #
    ######################################################################

    def get_start_period_br(self, data):
        return self._get_info(data, 'period_from', 'account.period')

    def get_end_period_br(self, data):
        return self._get_info(data, 'period_to', 'account.period')

    def get_fiscalyear_br(self, data):
        return self._get_info(data, 'fiscalyear_id', 'account.fiscalyear')

    def _get_chart_account_id_br(self, data):
        return self._get_info(data, 'chart_account_id', 'account.account')

    def _get_accounts_br(self, data):
        return self._get_info(data, 'account_ids', 'account.account')

    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field)
        if info:
            return self.pool.get(model).browse(self.cursor, self.uid, info)
        return False

    def _get_journals_br(self, data):
        return self._get_info(data, 'journal_ids', 'account.journal')

    def _get_display_account(self, data):
        val = self._get_form_param('display_account', data)
        if val == 'bal_all':
            return _('All accounts')
        elif val == 'bal_mix':
            return _('With transactions or non zero balance')
        else:
            return val

    def _get_display_partner_account(self, data):
        val = self._get_form_param('result_selection', data)
        if val == 'customer':
            return _('Receivable Accounts')
        elif val == 'supplier':
            return _('Payable Accounts')
        elif val == 'customer_supplier':
            return _('Receivable and Payable Accounts')
        else:
            return val

    def _get_display_target_move(self, data):
        val = self._get_form_param('target_move', data)
        if val == 'posted':
            return _('All Posted Entries')
        elif val == 'all':
            return _('All Entries')
        else:
            return val

    def _get_display_period_length(self, data):
        val = self._get_form_param('period_length', data)
        return val

    def _get_display_reconciled(self, data):
        val = self._get_form_param('reconcile_cond', data)
        if val == 'all':
            return _('All Items')
        elif val == 'open_item':
            return _('Open Items')
        elif val == 'reconciled':
            return _('Full Reconciled')
        else:
            return val

    def _get_display_account_raw(self, data):
        return self._get_form_param('display_account', data)

    def _get_filter(self, data):
        return self._get_form_param('filter', data)

    def _get_target_move(self, data):
        return self._get_form_param('target_move', data)

    def _get_initial_balance(self, data):
        return self._get_form_param('initial_balance', data)

    def _get_amount_currency(self, data):
        return self._get_form_param('amount_currency', data)

    def _get_date_from(self, data):
        return self._get_form_param('date_from', data)

    def _get_date_to(self, data):
        return self._get_form_param('date_to', data)

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)

    #############################################
    # Account and account line filter helper    #
    #############################################

    def sort_accounts_with_structure(self, root_account_ids, account_ids,
                                     context=None):
        """Sort accounts by code respecting their structure"""

        def recursive_sort_by_code(accounts, parent):
            sorted_accounts = []
            # add all accounts with same parent
            level_accounts = [account for account in accounts
                              if account['parent_id'] and
                              account['parent_id'][0] == parent['id']]
            # add consolidation children of parent, as they are logically on
            # the same level
            if parent.get('child_consol_ids'):
                level_accounts.extend([account for account in accounts
                                       if account['id']
                                       in parent['child_consol_ids']])
            # stop recursion if no children found
            if not level_accounts:
                return []

            level_accounts = sorted(level_accounts, key=lambda a: a['code'])

            for level_account in level_accounts:
                sorted_accounts.append(level_account['id'])
                sorted_accounts.extend(
                    recursive_sort_by_code(accounts, parent=level_account))
            return sorted_accounts

        if not account_ids:
            return []

        accounts_data = self.pool.get('account.account').read(
            self.cr, self.uid, account_ids,
            ['id', 'parent_id', 'level', 'code', 'child_consol_ids'],
            context=context)

        sorted_accounts = []

        root_accounts_data = [account_data for account_data in accounts_data
                              if account_data['id'] in root_account_ids]
        for root_account_data in root_accounts_data:
            sorted_accounts.append(root_account_data['id'])
            sorted_accounts.extend(
                recursive_sort_by_code(accounts_data, root_account_data))

        # fallback to unsorted accounts when sort failed
        # sort fails when the levels are miscalculated by account.account
        # check lp:783670
        if len(sorted_accounts) != len(account_ids):
            _logger.warn('Webkit financial reports: Sort of accounts failed.')
            sorted_accounts = account_ids

        return sorted_accounts

    def get_all_accounts(self, account_ids, exclude_type=None, only_type=None,
                         filter_report_type=None, context=None):
        """Get all account passed in params with their childrens

        @param exclude_type: list of types to exclude (view, receivable,
                                                payable, consolidation, other)
        @param only_type: list of types to filter on (view, receivable,
                                                payable, consolidation, other)
        @param filter_report_type: list of report type to filter on
        """
        context = context or {}
        accounts = []
        if not isinstance(account_ids, list):
            account_ids = [account_ids]
        acc_obj = self.pool.get('account.account')
        for account_id in account_ids:
            accounts.append(account_id)
            accounts += acc_obj._get_children_and_consol(
                self.cursor, self.uid, account_id, context=context)
        res_ids = list(set(accounts))
        res_ids = self.sort_accounts_with_structure(
            account_ids, res_ids, context=context)

        if exclude_type or only_type or filter_report_type:
            sql_filters = {'ids': tuple(res_ids)}
            sql_select = "SELECT a.id FROM account_account a"
            sql_join = ""
            sql_where = "WHERE a.id IN %(ids)s"
            if exclude_type:
                sql_where += " AND a.type not in %(exclude_type)s"
                sql_filters.update({'exclude_type': tuple(exclude_type)})
            if only_type:
                sql_where += " AND a.type IN %(only_type)s"
                sql_filters.update({'only_type': tuple(only_type)})
            if filter_report_type:
                sql_join += "INNER JOIN account_account_type t" \
                            " ON t.id = a.user_type"
                sql_join += " AND t.report_type IN %(report_type)s"
                sql_filters.update({'report_type': tuple(filter_report_type)})

            sql = ' '.join((sql_select, sql_join, sql_where))
            self.cursor.execute(sql, sql_filters)
            fetch_only_ids = self.cursor.fetchall()
            if not fetch_only_ids:
                return []
            only_ids = [only_id[0] for only_id in fetch_only_ids]
            # keep sorting but filter ids
            res_ids = [res_id for res_id in res_ids if res_id in only_ids]
        return res_ids

    ##########################################
    # Periods and fiscal years  helper       #
    ##########################################

    def _get_opening_periods(self):
        """Return the list of all journal that can be use to create opening
        entries.
        We actually filter on this instead of opening period as older version
        of OpenERP did not have this notion"""
        return self.pool.get('account.period').search(self.cursor, self.uid,
                                                      [('special', '=', True)])

    def exclude_opening_periods(self, period_ids):
        period_obj = self.pool.get('account.period')
        return period_obj.search(self.cr, self.uid, [['special', '=', False],
                                                     ['id', 'in', period_ids]])

    def get_included_opening_period(self, period, specific_report=False):
        """Return the opening included in normal period we use the assumption
        that there is only one opening period per fiscal year"""
        period_obj = self.pool.get('account.period')
        domain = [('special', '=', True),
                  ('date_start', '>=', period.date_start),
                  ('date_stop', '<=', period.date_stop),
                  ('company_id', '=', period.company_id.id)]
        p_ids = period_obj.search(self.cursor, self.uid, domain, limit=1)
        if specific_report:
            # PABI2
            opening_periods = period_obj.browse(self.cursor, self.uid, p_ids) \
                .filtered(lambda l: '00' in l.code).ids
            return opening_periods
        return p_ids

    def periods_contains_move_lines(self, period_ids):
        if not period_ids:
            return False
        mv_line_obj = self.pool.get('account.move.line')
        if isinstance(period_ids, (int, long)):
            period_ids = [period_ids]
        return mv_line_obj.search(self.cursor, self.uid,
                                  [('period_id', 'in', period_ids)], limit=1) \
            and True or False

    def _get_period_range_from_periods(self, start_period, stop_period,
                                       mode=None):
        """
        Deprecated. We have to use now the build_ctx_periods of period_obj
        otherwise we'll have inconsistencies, because build_ctx_periods does
        never filter on the the special
        """
        period_obj = self.pool.get('account.period')
        search_period = [('date_start', '>=', start_period.date_start),
                         ('date_stop', '<=', stop_period.date_stop)]

        if mode == 'exclude_opening':
            search_period += [('special', '=', False)]
        res = period_obj.search(self.cursor, self.uid, search_period)
        return res

    def _get_period_range_from_start_period(self, start_period,
                                            include_opening=False,
                                            fiscalyear=False,
                                            stop_at_previous_opening=False,
                                            specific_report=False):
        """We retrieve all periods before start period"""
        opening_period_id = False
        past_limit = []
        period_obj = self.pool.get('account.period')
        mv_line_obj = self.pool.get('account.move.line')
        # We look for previous opening period
        if stop_at_previous_opening:
            opening_search = [('special', '=', True),
                              ('date_stop', '<', start_period.date_start)]

            if fiscalyear:
                opening_search.append(('fiscalyear_id', '=', fiscalyear.id))

            opening_periods = period_obj.search(self.cursor, self.uid,
                                                opening_search,
                                                order='date_stop desc')
            for opening_period in opening_periods:
                validation_res = mv_line_obj.search(self.cursor,
                                                    self.uid,
                                                    [('period_id', '=',
                                                      opening_period)],
                                                    limit=1)
                if validation_res:
                    opening_period_id = opening_period
                    break
            if opening_period_id:
                # we also look for overlapping periods
                opening_period_br = period_obj.browse(
                    self.cursor, self.uid, opening_period_id)
                past_limit = [
                    ('date_start', '>=', opening_period_br.date_stop)]

        periods_search = [('date_stop', '<=', start_period.date_stop)]
        periods_search += past_limit

        if not include_opening:
            periods_search += [('special', '=', False)]

        if fiscalyear:
            periods_search.append(('fiscalyear_id', '=', fiscalyear.id))
        periods = period_obj.search(self.cursor, self.uid, periods_search)

        # PABI2
        if specific_report:
            periods = period_obj.browse(self.cursor, self.uid, periods)
            previous_periods = periods.filtered(
                lambda l: l.fiscalyear_id != start_period.fiscalyear_id).ids
            current_periods = periods.filtered(
                lambda l: l.fiscalyear_id == start_period.fiscalyear_id and
                l.code <= start_period.code).ids
            periods = previous_periods + current_periods

        if include_opening and opening_period_id:
            periods.append(opening_period_id)
        periods = list(set(periods))
        if start_period.id in periods:
            periods.remove(start_period.id)
        return periods

    def get_first_fiscalyear_period(self, fiscalyear, specific_report=False):
        return self._get_st_fiscalyear_period(
            fiscalyear, specific_report=specific_report)

    def get_last_fiscalyear_period(self, fiscalyear, specific_report=False):
        return self._get_st_fiscalyear_period(
            fiscalyear, order='DESC', specific_report=specific_report)

    def _get_st_fiscalyear_period(self, fiscalyear, special=False,
                                  order='ASC', specific_report=False):
        period_obj = self.pool.get('account.period')
        p_id = False
        if specific_report:
            # PABI2
            domain = [('fiscalyear_id', '=', fiscalyear.id)]
            if special:
                domain += [('special', '=', True)]
            p_id = period_obj.search(self.cursor, self.uid, domain,
                                     limit=1, order='code %s' % (order,))
        else:
            p_id = period_obj.search(self.cursor, self.uid,
                                     [('special', '=', special),
                                      ('fiscalyear_id', '=', fiscalyear.id)],
                                     limit=1, order='date_start %s' % (order,))
        if not p_id:
            raise osv.except_osv(_('No period found'), '')
        return period_obj.browse(self.cursor, self.uid, p_id[0])

    ###############################
    # Initial Balance helper      #
    ###############################

    def _compute_init_balance(self, account_id=None, period_ids=None,
                              mode='computed', default_values=False):
        if not isinstance(period_ids, list):
            period_ids = [period_ids]
        res = {}

        if not default_values:
            if not account_id or not period_ids:
                raise Exception('Missing account or period_ids')
            try:
                self.cursor.execute("SELECT sum(debit) AS debit, "
                                    " sum(credit) AS credit, "
                                    " sum(debit)-sum(credit) AS balance, "
                                    " sum(amount_currency) AS curr_balance"
                                    " FROM account_move_line"
                                    " WHERE period_id in %s"
                                    " AND account_id = %s",
                                    (tuple(period_ids), account_id))
                res = self.cursor.dictfetchone()

            except Exception:
                self.cursor.rollback()
                raise

        return {'debit': res.get('debit') or 0.0,
                'credit': res.get('credit') or 0.0,
                'init_balance': res.get('balance') or 0.0,
                'init_balance_currency': res.get('curr_balance') or 0.0,
                'state': mode}

    def _read_opening_balance(self, account_ids, start_period,
                              specific_report=False):
        """ Read opening balances from the opening balance
        """
        opening_period_selected = self.get_included_opening_period(
            start_period, specific_report=specific_report)
        if not opening_period_selected:
            raise osv.except_osv(
                _('Error'),
                _('No opening period found to compute the opening balances.\n'
                  'You have to configure a period on the first of January'
                  ' with the special flag.'))

        res = {}
        for account_id in account_ids:
            res[account_id] = self._compute_init_balance(
                account_id, opening_period_selected, mode='read')
        return res

    def _compute_initial_balances(self, account_ids, start_period, fiscalyear,
                                  specific_report=False):
        """We compute initial balance.
        If form is filtered by date all initial balance are equal to 0
        This function will sum pear and apple in currency amount if account as
        no secondary currency"""
        # if opening period is included in start period we do not need to
        # compute init balance we just read it from opening entries
        res = {}
        # PNL and Balance accounts are not computed the same way look for
        # attached doc We include opening period in pnl account in order to see
        # if opening entries were created by error on this account
        pnl_periods_ids = self._get_period_range_from_start_period(
            start_period, fiscalyear=fiscalyear, include_opening=True,
            specific_report=specific_report)
        bs_period_ids = self._get_period_range_from_start_period(
            start_period, include_opening=True, stop_at_previous_opening=True,
            specific_report=specific_report)

        opening_period_selected = self.get_included_opening_period(
            start_period, specific_report=specific_report)

        for acc in self.pool.get('account.account').browse(self.cursor,
                                                           self.uid,
                                                           account_ids):
            res[acc.id] = self._compute_init_balance(default_values=True)
            # Force period
            if opening_period_selected == start_period.ids:
                continue
            if acc.user_type.close_method == 'none':
                # we compute the initial balance for close_method == none only
                # when we print a GL during the year, when the opening period
                # is not included in the period selection!
                if pnl_periods_ids and not opening_period_selected:
                    res[acc.id] = self._compute_init_balance(
                        acc.id, pnl_periods_ids)
            else:
                res[acc.id] = self._compute_init_balance(acc.id, bs_period_ids)
        return res

    def _reconcile_cond_search(self, reconcile_cond, date_stop):
        domain = []
        if reconcile_cond and reconcile_cond != 'all':
            if reconcile_cond == 'open_item':
                if date_stop:
                    domain = ['|', ('date_reconciled', '=', False),
                              ('date_reconciled', '>', date_stop)]
                else:
                    domain = [('date_reconciled', '=', False)]
            elif reconcile_cond == 'reconciled':
                if date_stop:
                    domain = [('date_reconciled', '<=', date_stop)]
                else:
                    domain = [('date_reconciled', '!=', False)]
        return domain

    ################################################
    # Account move retrieval helper                #
    ################################################
    def _get_move_ids_from_periods(self, account_id, period_start, period_stop,
                                   target_move, reconcile_cond, charge_type,
                                   partner_ids=False, specific_report=False):
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        periods = []
        if specific_report:
            periods = self.build_ctx_periods(
                self.cursor, self.uid, period_start.id, period_stop.id)
        else:
            periods = period_obj.build_ctx_periods(
                self.cursor, self.uid, period_start.id, period_stop.id)
        if not periods:
            return []
        search = [
            ('period_id', 'in', periods), ('account_id', '=', account_id)]
        if target_move == 'posted':
            search += [('move_id.state', '=', 'posted')]

        # PABI2
        if partner_ids:
            search += [('partner_id', 'in', partner_ids)]
        if charge_type:
            search += [('charge_type', '=', charge_type)]
        search += self._reconcile_cond_search(reconcile_cond,
                                              period_stop.date_stop)
        # --

        return move_line_obj.search(self.cursor, self.uid, search)

    def _get_move_ids_from_dates(self, account_id, date_start, date_stop,
                                 target_move, reconcile_cond,
                                 charge_type, mode='include_opening',
                                 partner_ids=False):
        # TODO imporve perfomance by setting opening period as a property
        move_line_obj = self.pool.get('account.move.line')
        search_period = [('date', '>=', date_start),
                         ('date', '<=', date_stop),
                         ('account_id', '=', account_id)]

        # actually not used because OpenERP itself always include the opening
        # when we get the periods from january to december
        if mode == 'exclude_opening':
            opening = self._get_opening_periods()
            if opening:
                search_period += ['period_id', 'not in', opening]

        if target_move == 'posted':
            search_period += [('move_id.state', '=', 'posted')]

        # PABI2
        if partner_ids:
            search_period += [('partner_id', 'in', partner_ids)]
        if charge_type:
            search_period += [('charge_type', '=', charge_type)]
        search_period += self._reconcile_cond_search(reconcile_cond,
                                                     date_stop)
        # --

        return move_line_obj.search(self.cursor, self.uid, search_period)

    def get_move_lines_ids(self, account_id, main_filter, start, stop,
                           target_move,
                           reconcile_cond,  # PABI2
                           charge_type,
                           mode='include_opening',
                           partner_ids=False,
                           specific_report=False):
        """Get account move lines base on form data"""
        if mode not in ('include_opening', 'exclude_opening'):
            raise osv.except_osv(
                _('Invalid query mode'),
                _('Must be in include_opening, exclude_opening'))

        if main_filter in ('filter_period', 'filter_no'):
            return self._get_move_ids_from_periods(
                account_id, start, stop, target_move, reconcile_cond,
                charge_type, partner_ids=partner_ids,
                specific_report=specific_report)

        elif main_filter == 'filter_date':
            return self._get_move_ids_from_dates(account_id, start, stop,
                                                 target_move, reconcile_cond,
                                                 charge_type,
                                                 partner_ids=partner_ids)
        else:
            raise osv.except_osv(
                _('No valid filter'), _('Please set a valid time filter'))

    def _get_move_line_datas(self, move_line_ids,
                             order='per.special DESC, l.date ASC, \
                             per.date_start ASC, m.name ASC'):
        # Possible bang if move_line_ids is too long
        # We can not slice here as we have to do the sort.
        # If slice has to be done it means that we have to reorder in python
        # after all is finished. That quite crapy...
        # We have a defective desing here (mea culpa) that should be fixed
        #
        # TODO improve that by making a better domain or if not possible
        # by using python sort
        if not move_line_ids:
            return []
        if not isinstance(move_line_ids, list):
            move_line_ids = [move_line_ids]
        monster = """
SELECT l.id AS id,
            l.charge_type AS charge_type,
            l.date AS ldate,
            j.code AS jcode ,
            j.type AS jtype,
            l.currency_id,
            l.account_id,
            l.docline_seq AS item,
            l.amount_currency,
            l.ref AS lref,
            l.name AS lname,
            m.narration AS hname,
            j.name AS journal,
            (SELECT CONCAT(CASE WHEN cct.code IS NOT NULL THEN
                CONCAT('[',cct.code,'] ') ELSE '' END, CASE WHEN cct.name_short
                IS NOT NULL THEN cct.name_short WHEN cct.name
                IS NOT NULL THEN cct.name ELSE '' END) AS job_group
            FROM cost_control_type cct
            WHERE cct.id = (CASE WHEN l.cost_control_type_id IS NOT NULL
                THEN l.cost_control_type_id ELSE NULL END)) AS job_order_group,
            (SELECT CONCAT(CASE WHEN cc.code IS NOT NULL THEN
                CONCAT('[',cc.code,'] ') ELSE '' END, CASE WHEN cc.name_short
                IS NOT NULL THEN cc.name_short WHEN cc.name
                IS NOT NULL THEN cc.name ELSE '' END) AS job
            FROM cost_control cc
            WHERE cc.id = (CASE WHEN l.cost_control_id IS NOT NULL
                THEN l.cost_control_id ELSE NULL END)) AS job_order,
            (SELECT CONCAT(CASE WHEN pmp.code IS NOT NULL THEN
                CONCAT('[',pmp.code,'] ') ELSE '' END, CASE WHEN pmp.name_short
                IS NOT NULL THEN pmp.name_short WHEN pmp.name
                IS NOT NULL THEN pmp.name ELSE '' END) AS master
            FROM project_master_plan pmp
            WHERE pmp.id = (CASE WHEN rproject.master_plan_id IS NOT NULL
                THEN rproject.master_plan_id ELSE NULL END)) AS master_plan,
            (SELECT CONCAT(CASE WHEN rp.code IS NOT NULL THEN
                CONCAT('[',rp.code,'] ') ELSE '' END, CASE WHEN rp.name
                IS NOT NULL THEN rp.name ELSE '' END)
            FROM res_program rp
            WHERE rp.id = (CASE WHEN l.program_id IS NOT NULL
                THEN l.program_id ELSE NULL END)) AS program,
            (SELECT CONCAT(CASE WHEN aag.code IS NOT NULL THEN
                CONCAT('[',aag.code,'] ') ELSE '' END, CASE WHEN aag.name
                IS NOT NULL THEN aag.name ELSE '' END)
            FROM account_activity_group aag
            WHERE aag.id = (CASE WHEN l.activity_group_id IS NOT NULL
                THEN l.activity_group_id ELSE NULL END)) AS activity_group,
            (SELECT CONCAT(CASE WHEN aa.code IS NOT NULL THEN
                CONCAT('[',aa.code,'] ') ELSE '' END, CASE WHEN aa.name
                IS NOT NULL THEN aa.name ELSE '' END)
            FROM account_activity aa
            WHERE aa.id = (CASE WHEN l.activity_id IS NOT NULL
                THEN l.activity_id ELSE NULL END)) AS activity,
            (SELECT rp.display_name FROM res_users ru LEFT JOIN res_partner rp
             ON rp.id = ru.partner_id WHERE ru.id = m.write_uid LIMIT 1)
             AS posted_by,
            (SELECT CONCAT(CASE WHEN rsp.code IS NOT NULL THEN
                CONCAT('[',rsp.code,'] ') ELSE '' END, CASE WHEN rsp.name_short
                IS NOT NULL THEN rsp.name_short WHEN rsp.name
                IS NOT NULL THEN rsp.name ELSE '' END) AS master
            FROM res_section_program rsp
            WHERE rsp.id = (CASE WHEN l.section_program_id IS NOT NULL
                THEN l.section_program_id ELSE NULL END)) AS section_program,
            l.date_maturity AS due_date,
            rm.description AS mission,
            COALESCE(l.debit, 0.0) - COALESCE(l.credit, 0.0) AS balance,
            l.debit,
            l.credit,
            l.period_id AS lperiod_id,
            per.code as period_code,
            per.special AS peropen,
            l.partner_id AS lpartner_id,
            p.name AS partner_name,
            m.name AS move_name,
            COALESCE(partialrec.name, fullrec.name, '') AS rec_name,
            COALESCE(partialrec.id, fullrec.id, NULL) AS rec_id,
            m.id AS move_id,
            c.name AS currency_code,
            i.id AS invoice_id,
            i.type AS invoice_type,
            i.number AS invoice_number,
            l.date_maturity,
            m.date_document AS document_date,
            fisc.name AS fiscalyear,
            (SELECT CONCAT(CASE WHEN cv.code IS NOT NULL THEN
             CONCAT('[',cv.code,'] ') ELSE '' END, CASE WHEN cv.name_short
             IS NOT NULL THEN cv.name_short WHEN cv.name
             IS NOT NULL THEN cv.name ELSE '' END) AS budget
             FROM chartfield_view cv WHERE cv.model =
             (CASE WHEN l.section_id IS NOT NULL THEN 'res.section'
             WHEN l.project_id IS NOT NULL THEN 'res.project'
             WHEN l.invest_asset_id IS NOT NULL THEN 'res.invest.asset'
             WHEN l.invest_construction_phase_id IS NOT NULL
             THEN 'res.invest.construction.phase'
             WHEN l.personnel_costcenter_id IS NOT NULL
             THEN 'res.personnel.costcenter' ELSE NULL END)
             AND cv.res_id = (CASE WHEN l.section_id IS NOT NULL
             THEN l.section_id WHEN l.project_id IS NOT NULL
             THEN l.project_id WHEN l.invest_asset_id IS NOT NULL
             THEN l.invest_asset_id WHEN l.invest_construction_phase_id
             IS NOT NULL THEN l.invest_construction_phase_id
             WHEN l.personnel_costcenter_id IS NOT NULL
             THEN l.personnel_costcenter_id ELSE NULL END) LIMIT 1)
             AS budget_name,
            CONCAT(CASE WHEN rf.code IS NOT NULL THEN CONCAT('[',rf.code,'] ')
            ELSE '' END, CASE WHEN rf.name_short IS NOT NULL THEN rf.name_short
            WHEN rf.name IS NOT NULL THEN rf.name ELSE '' END)
            AS fund_name,
            CONCAT(CASE WHEN rc.code IS NOT NULL THEN CONCAT('[',rc.code,'] ')
            ELSE '' END, CASE WHEN rc.name_short IS NOT NULL THEN rc.name_short
            WHEN rc.name IS NOT NULL THEN rc.name ELSE '' END)
            AS costcenter_name,
            CONCAT(CASE WHEN rt.code IS NOT NULL THEN CONCAT('[',rt.code,'] ')
            ELSE '' END, CASE WHEN rt.name_short IS NOT NULL THEN rt.name_short
            WHEN rt.name IS NOT NULL THEN rt.name ELSE '' END)
            AS taxbranch_name,
            SUBSTRING(m.name, 1, 2) AS doctype,
            coalesce(fullrec.name, '') as reconcile_id,
            coalesce(partialrec.name, '') as partial_id,
            i.source_document
FROM account_move_line l
    JOIN account_move m on (l.move_id=m.id)
    LEFT JOIN res_currency c on (l.currency_id=c.id)
    LEFT JOIN account_move_reconcile partialrec
        on (l.reconcile_partial_id = partialrec.id)
    LEFT JOIN account_move_reconcile fullrec on (l.reconcile_id = fullrec.id)
    LEFT JOIN res_partner p on (l.partner_id=p.id)
    LEFT JOIN account_invoice i on (m.id =i.move_id)
    LEFT JOIN account_period per on (per.id=l.period_id)
    JOIN account_journal j on (l.journal_id=j.id)
    LEFT JOIN account_fiscalyear fisc on (per.fiscalyear_id=fisc.id)
    LEFT JOIN res_fund rf ON (l.fund_id = rf.id)
    LEFT JOIN res_costcenter rc ON (l.costcenter_id = rc.id)
    LEFT JOIN res_taxbranch rt ON (l.taxbranch_id = rt.id)
    LEFT JOIN res_project rproject ON (l.project_id = rproject.id)
    LEFT JOIN res_mission rm ON (l.mission_id = rm.id)
    WHERE l.id in %s"""
        monster += (" ORDER BY %s" % (order,))
        try:
            self.cursor.execute(monster, (tuple(move_line_ids),))
            res = self.cursor.dictfetchall()
        except Exception:
            self.cursor.rollback()
            raise
        return res or []

    def _get_moves_counterparts(self, move_ids, account_id, limit=3):
        if not move_ids:
            return {}
        if not isinstance(move_ids, list):
            move_ids = [move_ids]
        sql = """
SELECT account_move.id,
       array_to_string(
          ARRAY(SELECT DISTINCT a.code
                FROM account_move_line m2
                  LEFT JOIN account_account a ON (m2.account_id=a.id)
                WHERE m2.move_id =account_move_line.move_id
                  AND m2.account_id<>%s limit %s) , ', ')

FROM account_move
        JOIN account_move_line
            on (account_move_line.move_id = account_move.id)
        JOIN account_account
            on (account_move_line.account_id = account_account.id)
WHERE move_id in %s"""

        try:
            self.cursor.execute(sql, (account_id, limit, tuple(move_ids)))
            res = self.cursor.fetchall()
        except Exception:
            self.cursor.rollback()
            raise
        return res and dict(res) or {}

    def is_initial_balance_enabled(self, main_filter, specific_report=False):
        if specific_report:
            # PABI2
            if main_filter not in ('filter_period'):
                return False
        else:
            if main_filter not in ('filter_no', 'filter_year',
                                   'filter_period'):
                return False
        return True

    def _get_initial_balance_mode(self, start_period, specific_report=False):
        opening_period_selected = self.get_included_opening_period(
            start_period, specific_report=specific_report)
        # Force period
        if opening_period_selected == start_period.ids:
            opening_period_selected = []
        opening_move_lines = self.periods_contains_move_lines(
            opening_period_selected)
        if opening_move_lines:
            return 'opening_balance'
        else:
            return 'initial_balance'

    def build_ctx_periods(self, cr, uid, period_from_id, period_to_id):
        if period_from_id == period_to_id:
            return [period_from_id]
        Period = self.pool.get('account.period')
        period_from = Period.browse(cr, uid, period_from_id)
        period_date_start = period_from.date_start
        period_code_start = period_from.code
        company1_id = period_from.company_id.id
        period_to = Period.browse(cr, uid, period_to_id)
        period_date_stop = period_to.date_stop
        period_code_stop = period_to.code
        company2_id = period_to.company_id.id
        if company1_id != company2_id:
            raise osv.except_osv(
                _('Error!'),
                _('You should choose the periods '
                  'that belong to the same company.'))
        if period_date_start > period_date_stop:
            raise osv.except_osv(
                _('Error!'),
                _('Start period should precede then end period.'))
        return Period.search(
            cr, uid,
            [('date_start', '>=', period_date_start),
             ('date_stop', '<=', period_date_stop),
             ('code', '>=', period_code_start),
             ('code', '<=', period_code_stop)])
