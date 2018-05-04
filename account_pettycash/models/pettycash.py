# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountPettycash(models.Model):
    _name = 'account.pettycash'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Petty Cash Holder',
        domain=[('supplier', '=', True)],
        required=True,
    )
    pettycash_limit = fields.Float(
        string='Max Limit',
        default=0.0,
        required=True,
    )
    pettycash_balance = fields.Float(
        string='Balance',
        compute='_compute_pettycash_balance',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Petty Cash Account',
        domain=[('type', '!=', 'view'),
                ('user_type.report_type', '=', 'asset')],
        required=True,
    )
    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)',
         'Petty Cash Holder must be unique!'),
    ]

    @api.multi
    def _compute_pettycash_balance(self):
        Move = self.env['account.move.line']
        for rec in self:
            moves = Move.search([('partner_id', '=', rec.partner_id.id),
                                 ('account_id', '=', rec.account_id.id)])
            balance = sum([x.debit - x.credit for x in moves])
            rec.pettycash_balance = balance
