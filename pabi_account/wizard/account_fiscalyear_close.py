# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv

class AccountFiscalyearClose(models.TransientModel):
    _inherit = 'account.fiscalyear.close'

    @api.v7
    def data_save(self, cr, uid, ids, context=None):
        """
        This function close account fiscalyear and create entries in new fiscalyear
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs

        """
        def _reconcile_fy_closing(cr, uid, ids, context=None):
            """
            This private function manually do the reconciliation on the account_move_line given as `ids´, and directly
            through psql. It's necessary to do it this way because the usual `reconcile()´ function on account.move.line
            object is really resource greedy (not supposed to work on reconciliation between thousands of records) and
            it does a lot of different computation that are useless in this particular case.
            """
            #check that the reconcilation concern journal entries from only one company
            cr.execute('select distinct(company_id) from account_move_line where id in %s',(tuple(ids),))
            if len(cr.fetchall()) > 1:
                raise osv.except_osv(_('Warning!'), _('The entries to reconcile should belong to the same company.'))
            r_id = self.pool.get('account.move.reconcile').create(cr, uid, {'type': 'auto', 'opening_reconciliation': True})
            cr.execute('update account_move_line set reconcile_id = %s where id in %s',(r_id, tuple(ids),))
            # reconcile_ref deptends from reconcile_id but was not recomputed
            obj_acc_move_line._store_set_values(cr, uid, ids, ['reconcile_ref'], context=context)
            obj_acc_move_line.invalidate_cache(cr, uid, ['reconcile_id'], ids, context=context)
            return r_id

        obj_acc_period = self.pool.get('account.period')
        obj_acc_fiscalyear = self.pool.get('account.fiscalyear')
        obj_acc_journal = self.pool.get('account.journal')
        obj_acc_move = self.pool.get('account.move')
        obj_acc_move_line = self.pool.get('account.move.line')
        obj_acc_account = self.pool.get('account.account')
        obj_acc_journal_period = self.pool.get('account.journal.period')
        currency_obj = self.pool.get('res.currency')

        data = self.browse(cr, uid, ids, context=context)

        if context is None:
            context = {}
        fy_id = data[0].fy_id.id

        cr.execute("SELECT id FROM account_period WHERE date_stop < (SELECT date_start FROM account_fiscalyear WHERE id = %s)", (str(data[0].fy2_id.id),))
        fy_period_set = ','.join(map(lambda id: str(id[0]), cr.fetchall()))
        cr.execute("SELECT id FROM account_period WHERE date_start > (SELECT date_stop FROM account_fiscalyear WHERE id = %s)", (str(fy_id),))
        fy2_period_set = ','.join(map(lambda id: str(id[0]), cr.fetchall()))

        if not fy_period_set or not fy2_period_set:
            raise osv.except_osv(_('User Error!'), _('The periods to generate opening entries cannot be found.'))

        period = obj_acc_period.browse(cr, uid, data[0].period_id.id, context=context)
        new_fyear = obj_acc_fiscalyear.browse(cr, uid, data[0].fy2_id.id, context=context)
        old_fyear = obj_acc_fiscalyear.browse(cr, uid, fy_id, context=context)

        new_journal = data[0].journal_id.id
        new_journal = obj_acc_journal.browse(cr, uid, new_journal, context=context)
        company_id = new_journal.company_id.id

        if not new_journal.default_credit_account_id or not new_journal.default_debit_account_id:
            raise osv.except_osv(_('User Error!'),
                    _('The journal must have default credit and debit account.'))
        if (not new_journal.centralisation) or new_journal.entry_posted:
            raise osv.except_osv(_('User Error!'),
                    _('The journal must have centralized counterpart without the Skipping draft state option checked.'))

        #delete existing move and move lines if any
        move_ids = obj_acc_move.search(cr, uid, [
            ('journal_id', '=', new_journal.id), ('period_id', '=', period.id)])
        if move_ids:
            move_line_ids = obj_acc_move_line.search(cr, uid, [('move_id', 'in', move_ids)])
            obj_acc_move_line._remove_move_reconcile(cr, uid, move_line_ids, opening_reconciliation=True, context=context)
            obj_acc_move_line.unlink(cr, uid, move_line_ids, context=context)
            obj_acc_move.unlink(cr, uid, move_ids, context=context)

        cr.execute("SELECT id FROM account_fiscalyear WHERE date_stop < %s", (str(new_fyear.date_start),))
        result = cr.dictfetchall()
        fy_ids = [x['id'] for x in result]
        query_line = obj_acc_move_line._query_get(cr, uid,
                obj='account_move_line', context={'fiscalyear': fy_ids})
        #create the opening move
        vals = {
            'name': '/',
            'ref': '',
            'period_id': period.id,
            'date': period.date_start,
            'journal_id': new_journal.id,
        }
        move_id = obj_acc_move.create(cr, uid, vals, context=context)

        #1. report of the accounts with defferal method == 'unreconciled'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type = t.id)
            WHERE a.active
              AND a.type not in ('view', 'consolidation')
              AND a.company_id = %s
              AND t.close_method = %s''', (company_id, 'unreconciled', ))
        account_ids = map(lambda x: x[0], cr.fetchall())
        if account_ids:
            cr.execute('''
                INSERT INTO account_move_line (
                     name, create_uid, create_date, write_uid, write_date,
                     statement_id, journal_id, currency_id, date_maturity,
                     partner_id, blocked, credit, state, debit,
                     ref, account_id, period_id, date, move_id, amount_currency,
                     quantity, product_id, company_id,
                     charge_type
                     )
                  (SELECT name, create_uid, create_date, write_uid, write_date,
                     statement_id, %s,currency_id, date_maturity, partner_id,
                     blocked, credit, 'draft', debit, ref, account_id,
                     %s, (%s) AS date, %s, amount_currency, quantity, product_id, company_id,
                     charge_type
                   FROM account_move_line
                   WHERE account_id IN %s
                     AND ''' + query_line + '''
                     AND reconcile_id IS NULL)''', (new_journal.id, period.id, period.date_start, move_id, tuple(account_ids),))

            #We have also to consider all move_lines that were reconciled
            #on another fiscal year, and report them too
            cr.execute('''
                INSERT INTO account_move_line (
                     name, create_uid, create_date, write_uid, write_date,
                     statement_id, journal_id, currency_id, date_maturity,
                     partner_id, blocked, credit, state, debit,
                     ref, account_id, period_id, date, move_id, amount_currency,
                     quantity, product_id, company_id,
                     charge_type
                     )
                  (SELECT
                     b.name, b.create_uid, b.create_date, b.write_uid, b.write_date,
                     b.statement_id, %s, b.currency_id, b.date_maturity,
                     b.partner_id, b.blocked, b.credit, 'draft', b.debit,
                     b.ref, b.account_id, %s, (%s) AS date, %s, b.amount_currency,
                     b.quantity, b.product_id, b.company_id,
                     b.charge_type
                     FROM account_move_line b
                     WHERE b.account_id IN %s
                       AND b.reconcile_id IS NOT NULL
                       AND b.period_id IN ('''+fy_period_set+''')
                       AND b.reconcile_id IN (SELECT DISTINCT(reconcile_id)
                                          FROM account_move_line a
                                          WHERE a.period_id IN ('''+fy2_period_set+''')))''', (new_journal.id, period.id, period.date_start, move_id, tuple(account_ids),))
            self.invalidate_cache(cr, uid, context=context)

        #2. report of the accounts with defferal method == 'detail'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type = t.id)
            WHERE a.active
              AND a.type not in ('view', 'consolidation')
              AND a.company_id = %s
              AND t.close_method = %s''', (company_id, 'detail', ))
        account_ids = map(lambda x: x[0], cr.fetchall())

        if account_ids:
            cr.execute('''
                INSERT INTO account_move_line (
                     name, create_uid, create_date, write_uid, write_date,
                     statement_id, journal_id, currency_id, date_maturity,
                     partner_id, blocked, credit, state, debit,
                     ref, account_id, period_id, date, move_id, amount_currency,
                     quantity, product_id, company_id,
                     charge_type
                     )
                  (SELECT name, create_uid, create_date, write_uid, write_date,
                     statement_id, %s,currency_id, date_maturity, partner_id,
                     blocked, credit, 'draft', debit, ref, account_id,
                     %s, (%s) AS date, %s, amount_currency, quantity, product_id, company_id,
                     charge_type
                   FROM account_move_line
                   WHERE account_id IN %s
                     AND ''' + query_line + ''')
                     ''', (new_journal.id, period.id, period.date_start, move_id, tuple(account_ids),))
            self.invalidate_cache(cr, uid, context=context)

        #3. report of the accounts with defferal method == 'balance'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type = t.id)
            WHERE a.active
              AND a.type not in ('view', 'consolidation')
              AND a.company_id = %s
              AND t.close_method = %s''', (company_id, 'balance', ))
        account_ids = map(lambda x: x[0], cr.fetchall())

        query_1st_part = """
                INSERT INTO account_move_line (
                     debit, credit, name, date, move_id, journal_id, period_id,
                     account_id, currency_id, amount_currency, company_id, state,
                     charge_type
                     ) VALUES
        """
        query_2nd_part = ""
        query_2nd_part_args = []
        for account in obj_acc_account.browse(cr, uid, account_ids, context={'fiscalyear': fy_id}):
            company_currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id
            if not currency_obj.is_zero(cr, uid, company_currency_id, abs(account.balance)):
                if query_2nd_part:
                    query_2nd_part += ','
                query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                query_2nd_part_args += (account.balance > 0 and account.balance or 0.0,
                       account.balance < 0 and -account.balance or 0.0,
                       data[0].report_name,
                       period.date_start,
                       move_id,
                       new_journal.id,
                       period.id,
                       account.id,
                       account.currency_id and account.currency_id.id or None,
                       account.foreign_balance if account.currency_id else 0.0,
                       account.company_id.id,
                       'draft', 'external')
        if query_2nd_part:
            cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))
            self.invalidate_cache(cr, uid, context=context)

        #validate and centralize the opening move
        obj_acc_move.validate(cr, uid, [move_id], context=context)

        #reconcile all the move.line of the opening move
        ids = obj_acc_move_line.search(cr, uid, [('journal_id', '=', new_journal.id),
            ('period_id.fiscalyear_id','=',new_fyear.id)])
        if ids:
            reconcile_id = _reconcile_fy_closing(cr, uid, ids, context=context)
            #set the creation date of the reconcilation at the first day of the new fiscalyear, in order to have good figures in the aged trial balance
            self.pool.get('account.move.reconcile').write(cr, uid, [reconcile_id], {'create_date': new_fyear.date_start}, context=context)

        #create the journal.period object and link it to the old fiscalyear
        new_period = data[0].period_id.id
        ids = obj_acc_journal_period.search(cr, uid, [('journal_id', '=', new_journal.id), ('period_id', '=', new_period)])
        if not ids:
            ids = [obj_acc_journal_period.create(cr, uid, {
                   'name': (new_journal.name or '') + ':' + (period.code or ''),
                   'journal_id': new_journal.id,
                   'period_id': period.id
               })]
        cr.execute('UPDATE account_fiscalyear ' \
                    'SET end_journal_period_id = %s ' \
                    'WHERE id = %s', (ids[0], old_fyear.id))
        obj_acc_fiscalyear.invalidate_cache(cr, uid, ['end_journal_period_id'], [old_fyear.id], context=context)
        self._update_date_reconciled(cr, uid, ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def _update_date_reconciled(self, cr, uid, ids, context=None):
        cr.execute(
            '''
                select distinct reconcile_id
                from account_move_line
                    where reconcile_id is not null
                        and date_reconciled is null
            '''
        )
        result_ids = map(lambda x: x[0], cr.fetchall())
        if result_ids:
            cr.execute(
                '''
                    update account_move_line a
                    set date_reconciled = (
                        select max(date) from account_move_line
                            where reconcile_id = %s)
                            where reconcile_id = %s
                            and date_reconciled is null
                ''', (tuple(result_ids), (tuple(result_ids),))
            )
