# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import ChartField


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def write(self, vals, *args, **kargs):
        res = super(AccountMoveLine, self).write(vals, *args, **kargs)
        # Only do this if it is adjustment
        if self._context.get('is_move_adjustment', False):
            if not self._context.get('MyModelLoopBreaker', False):
                self.update_related_dimension(vals)
                for line in self:
                    Analytic = self.env['account.analytic.account']
                    analytic_account_id = \
                        Analytic.create_matched_analytic(line).id
                    line.with_context(MyModelLoopBreaker=True).write({
                        'analytic_account_id': analytic_account_id,
                    })
        return res

    @api.model
    def create(self, vals, *args, **kargs):
        res = super(AccountMoveLine, self).create(vals, *args, **kargs)
        # Only do this if it is adjustment
        if self._context.get('is_move_adjustment', False):
            if not self._context.get('MyModelLoopBreaker', False):
                res.update_related_dimension(vals)
            Analytic = self.env['account.analytic.account']
            res.analytic_account_id = \
                Analytic.create_matched_analytic(res)
        return res
