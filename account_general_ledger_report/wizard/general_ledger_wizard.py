# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountTrialBalanceWizard(models.TransientModel):
    _name = 'account.general.ledger.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        default=lambda self: self.env['account.fiscalyear'].find(),
        required=True,
    )
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        required=True,
        default='posted',
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        required=True,
        domain=[('type', '!=', 'view')],
    )
    amount_currency = fields.Boolean(
        string='With Currency',
        default=True,
    )
    reconcile_cond = fields.Selection(
        [('all', 'All Items'),
         ('open_item', 'Open Items'),
         ('reconciled', 'Full Reconciled')],
        default='all',
        required=True,
    )

    @api.multi
    def run_report(self):
        self.ensure_one()
        TB = self.env['account.general.ledger.report']
        report_id = TB.generate_report(self.fiscalyear_id.id,
                                       self.target_move,
                                       self.reconcile_cond,
                                       self.account_ids,
                                       self.amount_currency)
        action = self.env.ref('account_general_ledger_report.'
                              'action_account_general_ledger_report')
        result = action.read()[0]
        result.update({'res_id': report_id,
                       'domain': [('id', '=', report_id)]})
        return result
