# -*- coding: utf-8 -*-
from openerp import models, api


class AccountBankReceipt(models.Model):
    _inherit = "account.bank.receipt"

    @api.model
    def _prepare_move_line_vals(self, line):
        result = super(AccountBankReceipt, self)._prepare_move_line_vals(line)
        result.update(doc_ref=line.bank_receipt_id.name,
                      doc_id='%s,%s' % ('account.bank.receipt',
                                        line.bank_receipt_id.id))
        return result

    @api.model
    def _prepare_counterpart_move_lines_vals(
            self, receipt, total_debit, total_amount_currency):
        result = super(AccountBankReceipt, self
                       )._prepare_counterpart_move_lines_vals(
            receipt, total_debit, total_amount_currency)
        result.update(doc_ref=receipt.name,
                      doc_id='%s,%s' % ('account.bank.receipt', receipt.id))
        return result
