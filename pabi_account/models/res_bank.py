# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    active = fields.Boolean(
        default=True,
        help='Only for NSTDA, the new Bank Account has to get approved first. '
        'As such, it will default as False',
    )
    default = fields.Boolean(
        string='Default',
        default=False,
    )

    @api.model
    def create(self, vals):
        bank_acct = super(ResPartnerBank, self).create(vals)
        # Bank change history
        if bank_acct.partner_id:
            res = {'partner_id': bank_acct.partner_id.id,
                   'bank_account': bank_acct.acc_number,
                   'action': 'create', }
            self.env['res.partner.bank.change.history'].create(res)
        return bank_acct

    @api.multi
    def write(self, vals):
        if not self._context.get('bypass', False):
            for bank_acct in self:
                # Create change history
                if bank_acct.partner_id:
                    if 'create_history' in self._context and \
                            not self._context.get('create_history'):
                        continue
                    res = {'partner_id': bank_acct.partner_id.id,
                           'bank_account': bank_acct.acc_number,
                           'action': 'update', }
                    self.env['res.partner.bank.change.history'].create(res)
                # --
                # Set default, make sure, there will be only 1 default.
                if vals.get('default', False):
                    bank_acct.partner_id.bank_ids.with_context(bypass=True).\
                        write({'default': False})
                # --
        res = super(ResPartnerBank, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for bank_acct in self:
            if bank_acct.partner_id:  # only update for partner's bank
                res = {'partner_id': bank_acct.partner_id.id,
                       'bank_account': bank_acct.acc_number,
                       'action': 'delete'}
                self.env['res.partner.bank.change.history'].create(res)
        return super(ResPartnerBank, self).unlink()
