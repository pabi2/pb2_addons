# -*- coding: utf-8 -*-
from openerp import models


class BudgetReleaseWizard(models.TransientModel):
    _inherit = "budget.release.wizard"

    # # TODO: Should move to budget plan object?
    # @api.model
    # def _domain_release_pattern(self, plan):
    #   domain = super(BudgetReleaseWizard, self)._domain_release_pattern(plan)
    #     if plan._name in ('account.budget', 'account.budget.line'):
    #         domain.append(('type', '=', plan.chart_view))
    #     return domain

    # @api.model
    # def _get_release_pattern(self, plan):
    #     """ Overwrite """
    #     # Only for project_base, system need to cal start_period
    #     domain = self._domain_release_pattern(plan)
    #     budget_level = \
    #      self.env['account.fiscalyear.budget.level'].search(domain, limit=1)
    #     # Interval
    #     interval = budget_level.release_interval and \
    #         int(budget_level.release_interval) or 1
    #     start_period = 1
    #     is_auto_release = budget_level.is_auto_release
    #     # Project, calculate start_period
    #     if budget_level.type == 'project_base':
    #         # Only if project and a valid start date, calc start_period
    #         if (('project_id' in plan) and plan.project_id and
    #                 plan.project_id.date_start):
    #             date = plan.project_id.date_start
    #             fiscalyear_id = plan.fiscalyear_id.id
    #             periods = self.env['account.period'].search(
    #                 [('fiscalyear_id', '=', fiscalyear_id),
    #                  ('special', '=', False)], order='date_start').ids
    #             if len(periods) != 12:
    #               raise ValidationError(_('Error Fiscal Year != 12 Periods'))
    #             period = self.env['account.period'].find(date)[:1].id
    #             if period < min(periods):
    #                 start_period = 1
    #             if period > max(periods):
    #                 start_period = 100  # equal to unreachable
    #             if period in periods:
    #                 start_period = periods.index(period) + 1
    #     return interval, start_period, is_auto_release
