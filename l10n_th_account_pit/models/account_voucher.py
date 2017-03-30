# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    pit_line = fields.One2many(
        'personal.income.tax',
        'voucher_id',
        string='Tax Line PIT',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def proforma_voucher(self):
        for voucher in self:
            for line in voucher.pit_line:
                line.action_post()
        return super(AccountVoucher, self).proforma_voucher()

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            # Create the mirror only for those posted
            for line in voucher.pit_line.filtered('posted'):
                pit_line = line.copy({
                    'sequence': False,
                    'posted': False,
                    'amount_income': -line.amount_income,
                    'amount_wht': -line.amount_wht,
                })
                # Assign sequence and post
                pit_line.action_post()
        return super(AccountVoucher, self).cancel_voucher()
