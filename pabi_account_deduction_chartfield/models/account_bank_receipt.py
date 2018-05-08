# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.addons.account_budget_activity_rpt.models.account_activity \
    import ActivityCommon
from openerp.addons.pabi_chartfield.models.chartfield \
    import ChartFieldAction


class AccuontBankReceiptMultipleReconcile(ActivityCommon,
                                          ChartFieldAction,
                                          models.Model):
    _inherit = 'account.bank.receipt.multiple.reconcile'

    @api.model
    def create(self, vals):
        res = super(AccuontBankReceiptMultipleReconcile, self).create(vals)
        res.update_related_dimension(vals)
        return res

    # @api.one
    # @api.constrains('activity_group_id', 'activity_id', 'account_id')
    # def _check_account_activity(self):
    #     report_type = self.account_id.user_type.report_type
    #     if report_type in ('asset', 'liability') and \
    #             (self.activity_group_id or self.activity_id):
    #         raise ValidationError(
    #             _('Payment Diff, AG/A is not required for Balance Sheet'))
    #     if report_type not in ('asset', 'liability') and \
    #             not (self.activity_group_id and self.activity_id):
    #         raise ValidationError(
    #             _('Payment Diff, AG/A is required for Non-Balance Sheet'))


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    @api.multi
    def validate_bank_receipt(self):
        for receipt in self:
            for line in receipt.multiple_reconcile_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_id = \
                    Analytic.create_matched_analytic(line)
        res = super(AccountBankReceipt, self).validate_bank_receipt()
        return res
