# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.addons.account_budget_activity.models.account_activity \
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
