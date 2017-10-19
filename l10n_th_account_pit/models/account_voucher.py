# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    pit_line = fields.One2many(
        'personal.income.tax',
        'voucher_id',
        string='Tax Line PIT',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    pit_withhold = fields.Boolean(
        string='Withhold PIT',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def proforma_voucher(self):
        for voucher in self:
            if voucher.pit_line and voucher.tax_line_wht:
                raise ValidationError(_('WHT and PIT can not coexists!'))
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

    @api.onchange('pit_line')
    def _onchange_pit_line(self):
        if not self.pit_line:
            self.pit_withhold = False

    @api.onchange('pit_withhold')
    def _onchange_pit_withhold(self):
        self.pit_line = False
        if self.pit_withhold:
            pit_line = self.env['personal.income.tax'].new()
            pit_line.partner_id = self.partner_id
            # DO NOT DELETE: user don't want to auto calc, but we will.
            # pit_line.amount_income = self.amount - self.writeoff_amount
            # --
            # precalc_wht will be realized to amount_wht when validate doc.
            pit_line.precalc_wht = pit_line._calculate_pit_amount_wht(
                self.date, pit_line.partner_id.id, pit_line.amount_income)
            self.pit_line += pit_line

    # @api.model
    # def _validate_pit_to_deduction(self, voucher):
    #     if len(voucher.pit_line) != 1:
    #         raise ValidationError(
    #             _('> 1 PIT Line not allowed!'))
    #     if voucher.partner_id != voucher.pit_line[0].partner_id:
    #         raise ValidationError(
    #             _('Supplier in PIT line is different from the payment!'))

    # Do not delete yet.
    # @api.multi
    # def action_pit_to_deduction(self):
    #     for voucher in self:
    #         self._validate_pit_to_deduction(voucher)
    #         vals = {'voucher_id': voucher.id,
    #                 'account_id': 409,
    #                 'amount': -sum(voucher.pit_line.mapped('precalc_wht')),
    #                 'note': 'xxxx',
    #                 }
    #         self.env['account.voucher.multiple.reconcile'].create(vals)
