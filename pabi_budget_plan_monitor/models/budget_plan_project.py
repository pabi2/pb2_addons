# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_common import PrevFYCommon


class BudgetPlanProject(models.Model):
    _inherit = 'budget.plan.project'

    @api.multi
    def compute_prev_fy_performance(self):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        PrevFY = self.env['%s.prev.fy.view' % self._name]
        PrevFY._fill_prev_fy_performance(self)  # self = plans


class BudgetPlanProjectPrevFYView(PrevFYCommon, models.Model):
    """ Prev FY Performance view, must named as [model]+perv.fy.view """
    _name = 'budget.plan.project.prev.fy.view'
    _auto = False
    _description = 'Prev FY budget performance for project base'
    # Extra variable for this view
    _chart_view = 'project_base'
    _ex_view_fields = ['program_id', 'project_id']  # Each line
    _ex_domain_fields = ['program_id']  # Each plan is by this domain
    # TODO: what contion that we will not retrieve previous year data?
    # _ex_active_domain = [('project_id.state', '=', 'approve')]
    _ex_active_domain = []
    _filter_fy = 1  # Will the result of his view focus on prev fy only

    program_id = fields.Many2one(
        'res.program',
        string='Program',
        readonly=True,
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
    )

    @api.multi
    def _prepare_prev_fy_lines(self):
        """ Given search result from this view, prepare lines tuple """
        plan_lines = []
        plan_fiscalyear_id = self._context.get('plan_fiscalyear_id')
        Project = self.env['res.project']
        ProjectLine = self.env['budget.plan.project.line']
        project_fields = set(Project._fields.keys())
        plan_line_fields = set(ProjectLine._fields.keys())
        common_fields = list(project_fields & plan_line_fields)
        for rec in self:
            # Get commitment other than, the previous year.
            expenses = rec.project_id.monitor_expense_ids
            revenues = rec.project_id.monitor_revenue_ids

            all_actual_expense = sum(expenses.mapped('amount_actual'))
            all_actual_revenue = sum(revenues.mapped('amount_actual'))

            next_fy_ex = expenses.filtered(
                lambda l: l.fiscalyear_id.id == plan_fiscalyear_id)
            next_fy_commit = sum(next_fy_ex.mapped('amount_pr_commit') +
                                 next_fy_ex.mapped('amount_po_commit') +
                                 next_fy_ex.mapped('amount_exp_commit'))

            ytd_ex = expenses.filtered(
                lambda l: l.fiscalyear_id.date_start <=
                rec.fiscalyear_id.date_start)
            ytd_commit = sum(ytd_ex.mapped('amount_pr_commit') +
                             ytd_ex.mapped('amount_po_commit') +
                             ytd_ex.mapped('amount_exp_commit'))

            current_actual_revenue = sum(revenues.filtered(
                lambda l: l.fiscalyear_id == rec.fiscalyear_id
            ).mapped('amount_actual'))

            # 1) Begins
            val = {'c_or_n': 'continue',
                   'code': rec.project_id.code,
                   'name': rec.project_id.name,
                   'fund_id': rec.fund_id.id,
                   # some misc fields
                   'pm_employee': rec.project_id.pm_employee_id.name,
                   'analyst_employee': rec.project_id.analyst_employee_id.name,
                   'section': rec.project_id.pm_section_id.name,
                   'division': rec.project_id.owner_division_id.name,
                   'org': rec.project_id.org_id.name, }
            # 2) Project Info
            for field in common_fields:
                if field in rec.project_id and \
                        field not in ['id', '__last_update',
                                      'write_uid', 'write_date',
                                      'create_uid', 'create_date',
                                      'state',
                                      # Related fields should not get updated,
                                      # it unnecessary slow
                                      'program_id', 'section_program_id',
                                      'owner_division_id',
                                      ]:
                    try:
                        val[field] = rec.project_id[field].id
                    except:
                        val[field] = rec.project_id[field]
            # Calc from PABI2 monitoring views
            # 3) Overall
            val.update({'overall_revenue': all_actual_revenue,
                        'current_revenue': current_actual_revenue,
                        'overall_actual': all_actual_expense,
                        'overall_commit': ytd_commit,
                        'overall_expense_balance':
                        (val.get('overall_expense_budget', 0.0) -
                         all_actual_expense - ytd_commit), })
            # 4) Current Year
            val.update({
                'planned': rec.planned,
                'released': rec.released,
                'all_commit': rec.all_commit,
                'actual': rec.actual,
                'balance': rec.balance,
                'est_commit': next_fy_commit,  # from PO invoice plan
            })
            plan_lines.append((0, 0, val))
        return plan_lines
