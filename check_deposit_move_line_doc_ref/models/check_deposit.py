# -*- coding: utf-8 -*-
from openerp import models, api


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    @api.model
    def _prepare_move_line_vals(self, line):
        result = super(AccountCheckDeposit, self)._prepare_move_line_vals(line)
        result.update(doc_ref=line.check_deposit_id.name)
        return result

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, deposit, total_debit, total_amount_currency):
        result = super(AccountCheckDeposit, self
                       )._prepare_counterpart_move_lines_vals(
            deposit, total_debit, total_amount_currency)
        result.update(doc_ref=deposit.name)
        return result
