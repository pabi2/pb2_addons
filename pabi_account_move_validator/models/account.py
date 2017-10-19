# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.tools import float_compare
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        # Dr / Cr should be non zero
        self._validate_drcr_amount()
        self._validate_period_vs_date()
        # self.validate_activity_vs_account()  # Already check in ActiviCommon
        self._remove_zero_lines()
        res = super(AccountMove, self).post()
        return res

    @api.multi
    def _validate_drcr_amount(self):
        prec = self.env['decimal.precision'].precision_get('Account')
        for rec in self:
            lines = rec.line_id
            if not lines:
                continue
            debit = sum(lines.mapped('debit'))
            credit = sum(lines.mapped('credit'))
            if float_compare(debit, credit, prec) != 0:
                raise ValidationError(
                    _('Entry not balance, %s') % rec.ref)

    @api.multi
    def _validate_period_vs_date(self):
        Period = self.env['account.period']
        for rec in self:
            valid_period = Period.find(dt=rec.date)
            if rec.period_id != valid_period:
                raise ValidationError(
                    _('Period and date conflict on entry, %s') % rec.ref)

    @api.multi
    def _remove_zero_lines(self):
        move_lines = self.mapped('line_id')
        lines = move_lines.filtered(lambda l: not l.debit and not l.credit)
        lines.unlink()

    # Already check in activity common
    # @api.multi
    # def validate_activity_vs_account(self):
    #     for rec in self:
    #         lines = rec.line_id
    #         invalid_lines = lines.filtered(
    #             lambda l: l.activity_id and
    #             l.activity_id.account_id != l.account_id
    #         )
    #         for line in invalid_lines:
    #             raise ValidationError(
    #                 _('Account code "%s" not belong to activity %s!') %
    #                 (line.account_id.code, line.activity_id.name))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
