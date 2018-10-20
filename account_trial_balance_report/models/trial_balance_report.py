# -*- coding: utf-8 -*-
import datetime
from openerp import models, api, fields, _


class AccountTrailBalanceReport(models.Model):
    _name = 'account.trial.balance.report'

    name = fields.Char(
        string='Name',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    date_start = fields.Date(
        string='Start Date',
        readonly=True,
    )
    date_stop = fields.Date(
        string='End Date',
        readonly=True,
    )
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        string='Target Moves',
        readonly=True,
    )
    with_movement = fields.Boolean(
        string='With Movement',
        readonly=True,
    )
    line_ids = fields.One2many(
        'account.trial.balance.line',
        'report_id',
        string='Details'
    )

    @api.model
    def _get_moves(self, fiscalyear_id, date_start, date_stop,
                   target_move, with_movement):
        Account = self.env['account.account']
        Move = self.env['account.move.line']
        accounts = []
        # All moves, begin of this year until date_stop
        domain = [('period_id.fiscalyear_id', '=', fiscalyear_id),
                  ('date', '<=', date_stop)]
        if target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        moves = Move.search(domain)
        if with_movement:
            self._cr.execute("""
                select distinct aa.code, aa.id account_id
                from account_move_line aml
                join account_account aa on aa.id = aml.account_id
                and aml.id in %s
                order by aa.code
            """, (tuple(moves.ids), ))
            acct_ids = map(lambda x: x[1], self._cr.fetchall())
            accounts = Account.search([('id', 'in', acct_ids)], order='code')
        else:
            accounts = Account.search([('type', '!=', 'view')], order='code')
        return (accounts, moves)

    @api.model
    def _get_init_moves(self, report, account, target_move):
        MoveLine = self.env['account.move.line']
        domain = [('account_id', '=', account.id),
                  '|', ('centralisation', '!=', 'normal'),
                  '&', ('centralisation', '=', 'normal'),
                  ('date', '<', report.date_start), ]
        if target_move == 'posted':
            domain += [('move_id.state', '=', 'posted')]
        init_moves = MoveLine.search(domain)
        return init_moves

    @api.model
    def _get_focus_moves(self, report, account, target_move):
        MoveLine = self.env['account.move.line']
        domain = [('account_id', '=', account.id),
                  ('centralisation', '=', 'normal'),
                  ('date', '>=', report.date_start),
                  ('date', '<=', report.date_stop), ]
        if target_move == 'posted':
            domain += [('move_id.state', '=', 'posted')]
        focus_moves = MoveLine.search(domain)
        return focus_moves

    @api.model
    def generate_report(self, fiscalyear_id, date_start, date_stop,
                        target_move, with_movement):
        # Delete old reports
        self.search(
            [('create_uid', '=', self.env.user.id),
             ('create_date', '<', fields.Date.context_today(self))]).unlink()

        # Create report
        fiscalyear = self.env['account.fiscalyear'].browse(fiscalyear_id)
        name = 'Trial Balance %s' % fiscalyear.code
        report = self.create({'name': name,
                              'fiscalyear_id': fiscalyear_id,
                              'date_start': date_start,
                              'date_stop': date_stop,
                              'target_move': target_move,
                              'with_movement': with_movement})

        # Compute report lines
        accounts, moves = self._get_moves(fiscalyear_id, date_start, date_stop,
                                          target_move, with_movement)

        report_lines = []

        for account in accounts:
            init_moves = self._get_init_moves(report, account, target_move)
            focus_moves = self._get_focus_moves(report, account, target_move)
            initial = 0.0
            debit = 0.0
            credit = 0.0
            # Init
            if init_moves:
                self._cr.execute("""
                    select coalesce(sum(debit - credit), 0.0)
                    from account_move_line where id in %s
                """, (tuple(init_moves.ids),))
                initial = init_moves and self._cr.fetchone()[0]
            # Focus
            if focus_moves:
                self._cr.execute("""
                    select coalesce(sum(debit), 0.0) debit,
                        coalesce(sum(credit), 0.0) credit
                    from account_move_line where id in %s
                """, (tuple(focus_moves.ids),))
                res = self._cr.fetchone()
                (debit, credit) = (res[0], res[1])
            line_dict = {
                'account_id': account.id,
                'initial': initial,
                'debit': debit,
                'credit': credit,
                'balance': debit - credit,
                'final_balance': initial + (debit - credit),
            }
            report_lines.append((0, 0, line_dict))
        report.write({'line_ids': report_lines})
        return report.id

    @api.model
    def vacumm_old_reports(self):
        """ Vacumm report older than 1 day """
        old_date = datetime.datetime.now() - datetime.timedelta(days=1)
        reports = self.search([('create_date', '<',
                                old_date.strftime('%Y-%m-%d'))])
        reports.unlink()


class AccountTrailBalanceLine(models.Model):
    _name = 'account.trial.balance.line'

    report_id = fields.Many2one(
        'account.trial.balance.report',
        string='Report',
        index=True,
        ondelete='cascade',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Accont',
    )
    initial = fields.Float(
        string='Initial',
    )
    debit = fields.Float(
        string='Debit',
    )
    credit = fields.Float(
        string='Credit',
    )
    balance = fields.Float(
        string='Balance',
    )
    final_balance = fields.Float(
        string='Current Balance',
    )

    @api.multi
    def open_debit_items(self):
        return self.open_items('debit')

    @api.multi
    def open_credit_items(self):
        return self.open_items('credit')

    @api.multi
    def open_balance_items(self):
        return self.open_items('balance')

    @api.multi
    def open_final_balance_items(self):
        return self.open_items('final_balance')

    @api.multi
    def open_initial_items(self):
        return self.open_items('initial')

    @api.multi
    def open_items(self, move_type):
        self.ensure_one()
        TB = self.env['account.trial.balance.report']
        MoveLine = self.env['account.move.line']
        rpt = self.report_id
        _x, moves = TB._get_moves(rpt.fiscalyear_id.id,
                                  rpt.date_start, rpt.date_stop,
                                  rpt.target_move, rpt.with_movement)
        move_ids = []
        if move_type == 'debit':
            moves = TB._get_focus_moves(rpt, self.account_id, rpt.target_move)
            move_ids = MoveLine.search([('id', 'in', moves.ids),
                                        ('debit', '>', 0.0)]).ids
        if move_type == 'credit':
            moves = TB._get_focus_moves(rpt, self.account_id, rpt.target_move)
            move_ids = MoveLine.search([('id', 'in', moves.ids),
                                        ('credit', '>', 0.0)]).ids
        if move_type == 'balance':
            moves = TB._get_focus_moves(rpt, self.account_id, rpt.target_move)
            move_ids = moves.ids
        if move_type == 'initial':
            moves = TB._get_init_moves(rpt, self.account_id, rpt.target_move)
            move_ids = moves.ids
        if move_type == 'final_balance':
            init_moves = TB._get_init_moves(
                rpt, self.account_id, rpt.target_move)
            blance_moves = TB._get_focus_moves(
                rpt, self.account_id, rpt.target_move)
            move_ids = init_moves.ids + blance_moves.ids

        return {
            'name': _("Journal Items"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', 'in', move_ids)],
        }
