# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.addons.account_budget_activity_rpt.models.account_activity \
    import ActivityCommon
from openerp.addons.pabi_chartfield.models.chartfield \
    import ChartFieldAction


class AccuontVoucherMultipleReconcile(ActivityCommon,
                                      ChartFieldAction,
                                      models.Model):
    _inherit = 'account.voucher.multiple.reconcile'

    @api.model
    def create(self, vals):
        res = super(AccuontVoucherMultipleReconcile, self).create(vals)
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


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def action_move_line_create(self):
        for voucher in self:
            for line in voucher.multiple_reconcile_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_id = \
                    Analytic.create_matched_analytic(line)
        res = super(AccountVoucher, self).action_move_line_create()
        return res
