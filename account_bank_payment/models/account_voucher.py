# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    purchase_intransit = fields.Boolean(
        string='Purchase Bank Intransit',
        related='journal_id.purchase_intransit',
        readonly=True,
    )
    bank_payment_id = fields.Many2one(
        'account.bank.payment',
        string='Bank Payment',
        compute='_compute_bank_payment',
        store=True,
        readonly=True,
    )
    bank_payment_name = fields.Char(
        string='Bank Payment',
        related='bank_payment_id.name',
        readonly=True,
    )

    @api.model
    def _make_journal_search(self, ttype):
        res = super(AccountVoucher, self)._make_journal_search(ttype)
        context = self._context.copy()
        Journal = self.env['account.journal']
        if context.get('type', False) == 'payment':
            res = Journal.search([('type', '=', ttype),
                                  ('purchase_intransit', '=', True)], limit=1)
        return res

    @api.multi
    @api.depends('move_id.bank_payment_id')
    def _compute_bank_payment(self):
        for voucher in self:
            voucher.bank_payment_id = voucher.move_id.bank_payment_id

    @api.multi
    def action_open_bank_payment(self):
        self.ensure_one()
        action = self.env.ref('account_bank_payment.'
                              'action_bank_payment_tree')
        result = action.read()[0]
        result.update({'domain': [('id', '=', self.bank_payment_id.id)]})
        return result

    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            if voucher.type == 'payment' and voucher.purchase_intransit and \
                    self.env.user.company_id.auto_bank_payment:
                payment_date = fields.Date.context_today(self)
                voucher.move_id.create_bank_payment(payment_date)
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('type', False) == 'payment':
            Window = self.env['ir.actions.act_window']
            action = []
            if res.get('toolbar', False) and res.get('toolbar').get('action',
                                                                    False):
                for act in res.get('toolbar').get('action'):
                    window = Window.browse(act['id'])[0]
                    if 'bank_type' not in window.context:
                        action.append(act)
                    elif window.context == "{'bank_type': 'payment'}":
                        action.append(act)
                res['toolbar']['action'] = action
        return res
