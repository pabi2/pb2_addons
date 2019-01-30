# -*- coding: utf-8 -*-
from openerp import models, fields, api


class VoucherLoanAgreementDescription(models.TransientModel):
    _name = "voucher.loan.agreement.description"
    _description = "Loan Agreement Description"

    loan_agreement_description = fields.Text(
        string="Loan Agreement Description",
        size=1000,
        default=lambda self: self._default_loan_agreement_description(),
    )

    @api.model
    def _default_loan_agreement_description(self):
        active_id = self._context.get('active_id')
        voucher_line = self.env['account.voucher.line'].browse(active_id)
        description = voucher_line.loan_agreement_description
        return description

    @api.multi
    def action_save(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        voucher_line = self.env['account.voucher.line'].browse(active_id)
        voucher_line.loan_agreement_description = \
            self.loan_agreement_description
