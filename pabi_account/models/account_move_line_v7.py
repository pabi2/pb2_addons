# -*- coding: utf-8 -*-
import time
from openerp import workflow
from openerp.osv import osv
from openerp.tools.translate import _


class account_move_line(osv.osv):
    """ This overwrite is to make sure that, KV of AV can be cancelled """
    _inherit = 'account.move.line'

    def reconcile(self, cr, uid, ids, type='auto',
                  writeoff_acc_id=False, writeoff_period_id=False,
                  writeoff_journal_id=False, context=None):
        # HOOK
        hook_writeoff_move_id = False
        # --
        account_obj = self.pool.get('account.account')
        move_obj = self.pool.get('account.move')
        move_rec_obj = self.pool.get('account.move.reconcile')
        partner_obj = self.pool.get('res.partner')
        currency_obj = self.pool.get('res.currency')
        lines = self.browse(cr, uid, ids, context=context)
        unrec_lines = filter(lambda x: not x['reconcile_id'], lines)
        credit = debit = 0.0
        currency = 0.0
        account_id = False
        partner_id = False
        if context is None:
            context = {}
        company_list = []
        for line in lines:
            if company_list and line.company_id.id not in company_list:
                raise osv.except_osv(
                    _('Warning!'), _('To reconcile the entries company '
                                     'should be the same for all entries.'))
            company_list.append(line.company_id.id)
        for line in unrec_lines:
            if line.state != 'valid':
                raise osv.except_osv(
                    _('Error!'), _('Entry "%s" is not valid !') % line.name)
            credit += line['credit']
            debit += line['debit']
            currency += line['amount_currency'] or 0.0
            account_id = line['account_id']['id']
            partner_id = \
                (line['partner_id'] and line['partner_id']['id']) or False
        writeoff = debit - credit
        # Ifdate_p in context => take this date
        if 'date_p' in context and context['date_p']:
            date = context['date_p']
        else:
            date = time.strftime('%Y-%m-%d')

        cr.execute('SELECT account_id, reconcile_id '
                   'FROM account_move_line '
                   'WHERE id IN %s '
                   'GROUP BY account_id,reconcile_id',
                   (tuple(ids), ))
        r = cr.fetchall()
        # kittiu: remove this to cancle KV with reconcilable account > 1
        # if len(r) != 1:
        #     raise osv.except_osv(_('Error'),
        # _('Entries are not of the same account or already reconciled ! '))
        if not unrec_lines:
            raise osv.except_osv(
                _('Error!'), _('Entry is already reconciled.'))
        account = account_obj.browse(cr, uid, account_id, context=context)
        if not account.reconcile:
            raise osv.except_osv(
                _('Error'), _('The account is not defined to be reconciled !'))
        if r[0][1] is not None:
            raise osv.except_osv(
                _('Error!'), _('Some entries are already reconciled.'))

        is_zero_1 = currency_obj.is_zero(
            cr, uid, account.company_id.currency_id, writeoff)
        is_zero_2 = currency_obj.is_zero(
            cr, uid, account.currency_id, currency)
        if (not is_zero_1) or (account.currency_id and (not is_zero_2)):
            # DO NOT FORWARD PORT
            if not writeoff_acc_id:
                company = account.company_id
                if writeoff > 0:
                    writeoff_acc_id = \
                        company.expense_currency_exchange_account_id.id
                else:
                    writeoff_acc_id = \
                        company.income_currency_exchange_account_id.id
            if not writeoff_acc_id:
                raise osv.except_osv(
                    _('Warning!'), _('You have to provide an account for the '
                                     'write off/exchange difference entry.'))
            if writeoff > 0:
                debit = writeoff
                credit = 0.0
                self_credit = writeoff
                self_debit = 0.0
            else:
                debit = 0.0
                credit = -writeoff
                self_credit = 0.0
                self_debit = -writeoff
            # If comment exist in context, take it
            if 'comment' in context and context['comment']:
                libelle = context['comment']
            else:
                libelle = _('Write-Off')

            cur_obj = self.pool.get('res.currency')
            cur_id = False
            amount_currency_writeoff = 0.0
            if context.get('company_currency_id', False) != \
                    context.get('currency_id', False):
                cur_id = context.get('currency_id', False)
                for line in unrec_lines:
                    if line.currency_id and line.currency_id.id == \
                            context.get('currency_id', False):
                        amount_currency_writeoff += line.amount_currency
                    else:
                        tmp_amount = cur_obj.compute(
                            cr, uid, line.account_id.company_id.currency_id.id,
                            context.get('currency_id', False),
                            abs(line.debit-line.credit),
                            context={'date': line.date})
                        amount_currency_writeoff += \
                            (line.debit > 0) and tmp_amount or -tmp_amount

            writeoff_lines = [
                (0, 0, {
                    'name': libelle,
                    'debit': self_debit,
                    'credit': self_credit,
                    'account_id': account_id,
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': (amount_currency_writeoff and
                                        -1 * amount_currency_writeoff or
                                        (account.currency_id.id and
                                         -1 * currency or 0.0))
                }),
                (0, 0, {
                    'name': libelle,
                    'debit': debit,
                    'credit': credit,
                    'account_id': writeoff_acc_id,
                    'analytic_account_id': context.get('analytic_id', False),
                    'date': date,
                    'partner_id': partner_id,
                    'currency_id': cur_id or (account.currency_id.id or False),
                    'amount_currency': (amount_currency_writeoff and
                                        amount_currency_writeoff or
                                        (account.currency_id.id and
                                         currency or 0.0))
                })
            ]
            # DO NOT FORWARD PORT
            # In some exceptional situations (partial payment from a bank
            #   statement in foreign
            # currency), a write-off can be introduced at the very last moment
            #  due to currency
            # conversion. We record it on the bank statement account move.
            if context.get('bs_move_id'):
                writeoff_move_id = context['bs_move_id']
                for l in writeoff_lines:
                    self.create(cr, uid, dict(l[2], move_id=writeoff_move_id),
                                dict(context, novalidate=True))
                if not move_obj.validate(cr, uid, writeoff_move_id,
                                         context=context):
                    raise osv.except_osv(
                        _('Error!'),
                        _('You cannot validate a non-balanced entry.'))
            else:
                writeoff_move_id = move_obj.create(cr, uid, {
                    'period_id': writeoff_period_id,
                    'journal_id': writeoff_journal_id,
                    'date': date,
                    'state': 'draft',
                    'line_id': writeoff_lines
                })
                # HOOK
                hook_writeoff_move_id = writeoff_move_id
                # --

            writeoff_line_ids = self.search(
                cr, uid, [('move_id', '=', writeoff_move_id),
                          ('account_id', '=', account_id)])
            if account_id == writeoff_acc_id:
                writeoff_line_ids = [writeoff_line_ids[1]]
            ids += writeoff_line_ids

        # marking the lines as reconciled does not change
        #  their validity, so there is no need
        # to revalidate their moves completely.
        reconcile_context = dict(context, novalidate=True)
        r_id = move_rec_obj.create(cr, uid, {'type': type},
                                   context=reconcile_context)
        self.write(cr, uid, ids, {'reconcile_id': r_id,
                                  'reconcile_partial_id': False},
                   context=reconcile_context)

        # the id of the move.reconcile is written
        #   in the move.line (self) by the create method above
        # because of the way the line_id are defined: (4, x, False)
        for id in ids:
            workflow.trg_trigger(uid, 'account.move.line', id, cr)

        if lines and lines[0]:
            partner_id = lines[0].partner_id and \
                lines[0].partner_id.id or False
            if partner_id and not partner_obj.has_something_to_reconcile(
                    cr, uid, partner_id, context=context):
                partner_obj.mark_as_reconciled(cr, uid, [partner_id],
                                               context=context)

        # HOOK, with this context no partner in new writeoff move line
        # To by pass constraint _check_reconcile_same_partner()
        # We use SQL to update move line
        if hook_writeoff_move_id:
            if context.get('force_partner_id', False):
                cr.execute("""
                    update account_move set partner_id = %s, ref = %s
                    where id = %s
                """, (context['force_partner_id'],
                      context.get('force_comment'),
                      hook_writeoff_move_id))
                cr.execute("""
                    update account_move_line set partner_id = %s, ref = %s
                    where move_id = %s
                """, (context['force_partner_id'],
                      context.get('force_comment'),
                      hook_writeoff_move_id))
            else:
                cr.execute("""
                    update account_move set partner_id = null, ref = %s
                    where id = %s
                """, (context.get('force_comment'), hook_writeoff_move_id, ))
                cr.execute("""
                    update account_move_line set partner_id = null, ref = %s
                    where move_id = %s
                """, (context.get('force_comment'), hook_writeoff_move_id, ))
        # Chartifled, write it
        if hook_writeoff_move_id and context.get('force_chartfield_id', False):
            chartfield = self.pool.get('chartfield.view').\
                browse(cr, uid, context['force_chartfield_id'])
            update_sql = False
            if chartfield.type == 'sc:':
                update_sql = 'section_id = %s' % chartfield.res_id
            if chartfield.type == 'pj:':
                update_sql = 'project_id = %s' % chartfield.res_id
            if chartfield.type == 'cp:':
                update_sql = \
                    'invest_construction_phase_id = %s' % chartfield.res_id
            if chartfield.type == 'ia:':
                update_sql = 'invest_asset_id = %s' % chartfield.res_id
            if chartfield.type == 'pc:':
                update_sql = 'personnel_costcenter_id = %s' % chartfield.res_id
            if update_sql:
                cr.execute("""
                    update account_move_line set %s where move_id = %s
                """ % (update_sql, hook_writeoff_move_id))
        # --
        return r_id

    def _update_journal_check(
            self, cr, uid, journal_id, period_id, context=None):
        if context is None:
            context = {}
        clear_prepaid = context.get('is_clear_prepaid', False)
        reverse_move = context.get('reverse_move', False)
        if reverse_move or clear_prepaid:
            return True
        return super(account_move_line, self)._update_journal_check(
            cr, uid, journal_id, period_id, context=context)
