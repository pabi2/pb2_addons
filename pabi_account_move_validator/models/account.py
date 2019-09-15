# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.tools.float_utils import float_compare
from openerp.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        # Dr / Cr should be non zero
        self._validate_drcr_amount()
        self._validate_period_vs_date()
        # self._remove_zero_lines()  # Do not remove, may bring back
        res = super(AccountMove, self).post()
        return res

    @api.multi
    def _validate_drcr_amount(self):
        prec = self.env['decimal.precision'].precision_get('Account')
        for rec in self:
            lines = rec.line_id
            if not lines:
                continue
            # kittiu: change from using mapped to direct sql for more accuracy
            # --
            # debit = sum(lines.mapped('debit'))
            # credit = sum(lines.mapped('credit'))
            self._cr.execute("""
                select sum(debit), sum(credit)
                from account_move_line where move_id = %s
            """, (rec.id, ))
            res = self._cr.fetchall()[0]
            debit, credit = res[0], res[1]
            # --
            if float_compare(debit, credit, prec) != 0:
                raise ValidationError(
                    _('Entry not balance, %s') % rec.ref)

    @api.multi
    def _validate_period_vs_date(self):
        for rec in self:
            if rec.period_id:
                if not (rec.date >= rec.period_id.date_start and
                        rec.date <= rec.period_id.date_stop):
                    raise ValidationError(
                        _('Period and date conflict on entry, %s') % rec.ref)
        return True

    @api.multi
    def _remove_zero_lines(self):
        move_lines = self.mapped('line_id')
        lines = move_lines.filtered(lambda l: not l.debit and
                                    not l.credit and not l.product_id)
        lines.unlink()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
