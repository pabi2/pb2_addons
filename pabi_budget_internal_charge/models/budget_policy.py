# -*- coding: utf-8 -*-
from openerp import models, api


# THIS MAY NEED TO BE MODIFIED, AS WE CHANGED MODEL ALREADY

# class BudgetFiscalPolicy(models.Model):
#     _inherit = "budget.fiscal.policy"
#
#     @api.model
#     def _get_unit_budget_policy_sql(self):
#         """ Overwrite, as we only want external expense """
#         sql = """
#             select tmpl.chart_view, tmpl.org_id,
#             sum(bpu.planned_expense_external) as planned_expense  -- HERE
#             from budget_plan_unit bpu
#             join budget_plan_template tmpl on tmpl.id = bpu.template_id
#             where tmpl.fiscalyear_id = %s and tmpl.state = 'accept_corp'
#             group by tmpl.chart_view, tmpl.org_id
#         """
#         return sql
#
#     @api.model
#     def _prepare_breakdown_line(self, structure, plan, breakdown):
#         vals = super(BudgetFiscalPolicy, self).\
#             _prepare_breakdown_line(structure, plan, breakdown)
#         if structure == 'unit':  # For unit base care only external
#             vals.update({'planned_amount': plan.planned_expense_external})
#         return vals
