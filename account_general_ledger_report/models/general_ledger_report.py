# -*- coding: utf-8 -*-
from lxml import etree
import datetime
from openerp import models, api, fields, _


class AccountGeneralLedgerReport(models.Model):
    _name = 'account.general.ledger.report'

    name = fields.Char(
        string='Name',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        string='Target Moves',
    )
    reconcile_cond = fields.Selection(
        [('all', 'All Items'),
         ('open_item', 'Open Items'),
         ('reconciled', 'Full Reconciled')],
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        required=True,
    )
    amount_currency = fields.Boolean(
        string='With Currency',
        default=True,
    )
    line_ids = fields.One2many(
        'account.general.ledger.line',
        'report_id',
        string='Details'
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    org_ids = fields.Many2many(
        'res.org', string='Org',
    )

    @api.model
    def _get_moves(self, fiscalyear_id, target_move, reconcile_cond,
                   account_ids, amount_currency, charge_type, org_ids):
        period = self.env['account.period']
        move = self.env['account.move.line']
        fiscalyear = self.env['account.fiscalyear'].browse(fiscalyear_id)
        periods = []
        # All moves, begin of this year until date_stop
        domain = [('period_id.fiscalyear_id', '=', fiscalyear_id),
                  ('account_id', 'in', account_ids.ids)]
        if charge_type:
            domain.append(('charge_type', '=', charge_type))
        if org_ids:  #tangkwa 26/03/2019
            domain.append(('org_id', 'in', org_ids.ids))
        if target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        if reconcile_cond == 'open_item':
            domain.append(('reconcile_id', '=', False))
        if reconcile_cond == 'reconciled':
            domain.append(('reconcile_id', '!=', False))
        moves = move.search(domain)

        self._cr.execute("""
            SELECT ap.id AS period_id, ap.name
                FROM account_period ap
                WHERE ap.fiscalyear_id = '%s'
                ORDER BY ap.id
        """ % (fiscalyear.id))
        period_ids = map(lambda x: x[0], self._cr.fetchall())
        periods = period.search(
            [('id', 'in', period_ids)], order='code')
        return (periods, moves)

    @api.model
    def _get_period_moves(self, report, period):
        moveLine = self.env['account.move.line']
        period_moves = moveLine.search(
            [('period_id.fiscalyear_id', '=', report.fiscalyear_id.id),
             ('period_id.date_start', '<', period.date_start)])
        return period_moves

    @api.model
    def _get_focus_moves(self, moves, period):
        moveLine = self.env['account.move.line']
        focus_moves = moveLine.search(
            [('period_id', '=', period.id),
             ('id', 'in', moves.ids)])
        return focus_moves

    @api.model
    def generate_report(self, fiscalyear_id, target_move, reconcile_cond,
                        account_ids, amount_currency, charge_type,org_ids):
        # Delete old reports
        self.search(
            [('create_uid', '=', self.env.user.id),
             ('create_date', '<', fields.Date.context_today(self))]).unlink()

        # Create report
        name = 'General Ledger (Web)'
        report = self.create({'name': name,
                              'fiscalyear_id': fiscalyear_id,
                              'target_move': target_move,
                              'reconcile_cond': reconcile_cond,
                              'account_ids': [(6, 0, account_ids.ids)],
                              'amount_currency': amount_currency,
                              'charge_type': charge_type,
                              'org_ids': [(6, 0, org_ids.ids)],
                              })
        # Compute report lines
        periods, moves = self._get_moves(fiscalyear_id, target_move,
                                         reconcile_cond, account_ids,
                                         amount_currency, charge_type,
                                         org_ids)

        report_lines = []
        accum = 0.0

        for period in periods:
            focus_moves = self._get_focus_moves(moves, period)
            debit = 0.0
            credit = 0.0
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
                'period_id': period.id,
                'debit': debit,
                'credit': credit,
                'balance': debit - credit,
                'accum_balance': accum + (debit - credit),
            }
            accum = line_dict.get('accum_balance')
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


class AccountGeneralLedgerLine(models.Model):
    _name = 'account.general.ledger.line'

    report_id = fields.Many2one(
        'account.general.ledger.report',
        string='Report',
        index=True,
        ondelete='cascade',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
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
    accum_balance = fields.Float(
        string='Accum.Balance',
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
    def open_accum_balance_items(self):
        return self.open_items('accum_balance')

    @api.multi
    def open_items(self, move_type):
        self.ensure_one()
        TB = self.env['account.general.ledger.report']
        moveLine = self.env['account.move.line']
        rpt = self.report_id
        _x, moves = TB._get_moves(rpt.fiscalyear_id.id, rpt.target_move,
                                  rpt.reconcile_cond, rpt.account_ids,
                                  rpt.amount_currency, rpt.charge_type,
                                  rpt.org_ids)
        move_ids = []
        if move_type == 'debit':
            moves = TB._get_focus_moves(moves, self.period_id)
            move_ids = moveLine.search([('id', 'in', moves.ids),
                                        ('debit', '>', 0.0)]).ids
        if move_type == 'credit':
            moves = TB._get_focus_moves(moves, self.period_id)
            move_ids = moveLine.search([('id', 'in', moves.ids),
                                        ('credit', '>', 0.0)]).ids
        if move_type == 'balance':
            moves = TB._get_focus_moves(moves, self.period_id)
            move_ids = moves.ids
        if move_type == 'accum_balance':
            period_moves = TB._get_period_moves(rpt, self.period_id)
            blance_moves = TB._get_focus_moves(moves, self.period_id)
            move_ids = blance_moves.ids + period_moves.ids

        return {
            'name': _("Journal Items"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'context': self._context,
                        'currency': rpt.amount_currency,
                        'amount_currency': rpt.amount_currency},
            'nodestroy': True,
            'domain': [('id', 'in', move_ids)],

        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(AccountMoveLine, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        model = self._context.get('active_model', False)
        if model == 'account.general.ledger.line' and view_type == 'tree':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("/tree")
            for node in nodes:
                node.set('create', 'false')
                node.set('edit', 'false')
                node.set('delete', 'false')
            res['arch'] = etree.tostring(doc)
        return res
