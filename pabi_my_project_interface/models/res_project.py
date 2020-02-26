# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError
from openerp.addons.document_status_history.models.document_history import \
    LogCommon
from openerp.tools.float_utils import float_compare


class ResProject(LogCommon, models.Model):
    _inherit = 'res.project'

    @api.multi
    def _release_fiscal_budget(self, fiscalyear, released_amount):
        """ Distribute budget released to all AG of the same year
            by distribute to the first AG first,
            show warning if released amount > planned amout
        """
        # Not current year, no budget release allowed
        current_fy = self.env['account.fiscalyear'].find()
        release_external_budget = fiscalyear.control_ext_charge_only
        ignore_current_fy = self._context.get('ignore_current_fy_lock', False)
        for project in self.sudo():
            if project.current_fy_release_only and \
                    current_fy != fiscalyear.id and \
                    not ignore_current_fy:
                raise ValidationError(
                    _('Not allow to release budget for fiscalyear %s!\nOnly '
                      'current year budget is allowed.' % fiscalyear.name))
            budget_plans = project.budget_plan_ids.filtered(lambda l: l.fiscalyear_id == fiscalyear)
            budget_monitor = project.monitor_expense_ids.filtered(lambda l: l.fiscalyear_id == fiscalyear and l.budget_method=='expense' and l.charge_type=='external')
            budget_plans.write({'released_amount': 0.0})  # Set zero
            if release_external_budget:  # Only for external charge
                budget_plans = budget_plans.filtered(
                    lambda l: l.charge_type == 'external'
                    and l.budget_method == 'expense')
            if not budget_plans:
                raise ValidationError(
                    _('Not allow to release budget for project without plan!'))
            planned_amount = sum([x.planned_amount for x in budget_plans])
            consumed_amount = sum([x.amount_consumed for x in budget_monitor])
            if float_compare(released_amount, planned_amount, 2) == 1 and \
                    not ignore_current_fy:
                raise ValidationError(
                    _('Releasing budget (%s) > planned (%s)!' %
                      ('{:,.2f}'.format(released_amount),
                       '{:,.2f}'.format(planned_amount))))
            if float_compare(released_amount, consumed_amount, 2) == -1 and \
                    not ignore_current_fy:
                raise ValidationError(
                    _('Releasing budget (%s) < Consumed Amount (%s)!' %
                      ('{:,.2f}'.format(released_amount),
                       '{:,.2f}'.format(consumed_amount))))
            remaining = released_amount
            update_vals = []
            for budget_plan in budget_plans:
                # remaining > planned_amount in line
                if float_compare(remaining,
                                 budget_plan.planned_amount, 2) == 1:
                    # expense only
                    if not budget_plan.planned_amount \
                            and budget_plan.budget_method == 'expense':
                        update = {'released_amount': remaining}
                        update_vals.append((1, budget_plan.id, update))
                        break
                    update = {'released_amount': budget_plan.planned_amount}
                    # case : last line
                    if budget_plan.id == budget_plans[-1].id:
                        update = {'released_amount': remaining}
                    remaining -= budget_plan.planned_amount
                    update_vals.append((1, budget_plan.id, update))
                else:
                    update = {'released_amount': remaining}
                    remaining = 0.0
                    update_vals.append((1, budget_plan.id, update))
                    break
            if update_vals:
                project.write({'budget_plan_ids': update_vals})
        return True
