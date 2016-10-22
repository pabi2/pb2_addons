# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError


class ApproveBankAccountWizard(models.TransientModel):
    _name = "approve.bank.account.wizard"

    approved = fields.Boolean(
        string='Approved',
        default=lambda s: s.env['res.partner.bank'].
        browse(s._context.get('active_id')).active
    )
    note = fields.Text(
        string='Notes'
    )

    @api.model
    def _validate_approve_user(self):
        if self.env.user not in \
                self.env.user.company_id.bank_account_approver_ids:
            raise UserError(
                _('You are not allowed to approve / unapprove bank account!'))
        return

    @api.multi
    def approve(self):
        self.ensure_one()
        self._validate_approve_user()
        active_id = self._context.get('active_id')
        bank_acct = self.env['res.partner.bank'].browse(active_id)
        bank_acct.with_context(create_history=False).write({'active': True})
        res = {'partner_id': bank_acct.partner_id.id,
               'bank_account': bank_acct.acc_number,
               'action': 'approve',
               'note': self.note,
               }
        self.env['res.partner.bank.change.history'].create(res)
        # If this parter do not have default account yet, use this one.
        default_account = bank_acct.partner_id.bank_ids.filtered('default')
        if not default_account:
            bank_acct.default = True
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def unapprove(self):
        self.ensure_one()
        self._validate_approve_user()
        active_id = self._context.get('active_id')
        bank_acct = self.env['res.partner.bank'].browse(active_id)
        bank_acct.with_context(create_history=False).write({'active': False})
        res = {'partner_id': bank_acct.partner_id.id,
               'bank_account': bank_acct.acc_number,
               'action': 'unapprove',
               'note': self.note,
               }
        self.env['res.partner.bank.change.history'].create(res)
        bank_acct.default = False
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
