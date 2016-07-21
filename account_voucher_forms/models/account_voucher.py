# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    cheque_no = fields.Char('Cheque No.')
    bank_branch = fields.Char('Bank/Branch')
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        copy=False,
    )

    @api.multi
    def action_move_line_create(self):
        res = super(AccountVoucher, self).action_move_line_create()
        for voucher in self:
            voucher.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.today()})
        return res
