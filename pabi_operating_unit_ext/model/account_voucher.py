# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )

    @api.one
    @api.constrains('operating_unit_id', 'journal_id', 'type')
    def _check_journal_account_operating_unit(self):
        """ Overwrite, as we no longer need to check """
        return True


class AccountVoucherLine(models.Model):
    _inherit = "account.voucher.line"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
