# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    # Special field for my project
    project_plan_ids = fields.One2many(
        'res.project.budget.plan',
        'budget_id',
        string='Project Budget Plan',
    )
    project_auto_sync = fields.Boolean(
        string='Auto Sync',
        default=True,
        help="Auto sync with poject plan as soon as related project is updated"
    )

    @api.multi
    def sync_budget_my_project(self):
        """ This method pull the project's budget plan and update
        this budget's line.
        After synced, the synced = True, and it won't be pulled again.
        When phase is updated, it will reset synced = False, and ready for sync
        """
        self.ensure_one()  # Make sure it is synced one by one
        if self.chart_view != 'project_base':
            raise ValidationError(_('Not a project based budget control'))
        # Find matched phases for this budget control
        Project = self.env['res.project']
        BudgetLine = self.env['account.budget.line']
        projects = Project.search([('program_id', '=', self.program_id.id)])
        # Clear budget_line without sync ref (myproject, we can't create here)
        prj_budget_lines = self.project_plan_ids.mapped('sync_budget_line_id')
        diff_lines = self.budget_line_ids - prj_budget_lines
        diff_lines.unlink()
        if self._context.get('project_id', False):
            projects = Project.search([('id', '=',
                                        self._context['project_id'])])
        for project in projects:
            # If sync only 1 specific project, passed from res.project
            if 'project_id' in self._context and \
                    project.id != self._context.get('project_id'):
                continue
            for project_plan in project.budget_plan_ids.\
                    filtered(lambda l: l.fiscalyear_id == self.fiscalyear_id):
                # Create budget control line if not exists
                if not project_plan.sync_budget_line_id:
                    budget_line_dict = {
                        'budget_id': self.id,
                        'activity_group_id': project_plan.activity_group_id.id,
                        'charge_type': project_plan.charge_type,
                        'budget_method': project_plan.budget_method,
                        'income_section_id': project_plan.income_section_id.id,
                        'project_id': project.id,
                        'fund_id': (project.fund_ids and
                                    project.fund_ids[0].id or False),
                    }
                    budget_line = BudgetLine.create(budget_line_dict)
                    budget_line.update_related_dimension(budget_line_dict)
                    project_plan.sync_budget_line_id = budget_line
        # Sync all projects in one go
        projects.sync_project_plan_to_budget_line([self.fiscalyear_id.id])
        # Recompute overall budgetted expense and revenue
        self._compute_budgeted_overall()
        return True

    @api.model
    def generate_project_base_controls(self, fiscalyear_id=None):
        control_ids = super(AccountBudget, self).\
            generate_project_base_controls(fiscalyear_id=fiscalyear_id)
        # First sync with myProject
        for control in self.browse(control_ids):
            control.sync_budget_my_project()
        return control_ids


class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    @api.multi
    def unlink(self):
        # unlinked line, reset the sync
        if self.ids:
            self._cr.execute("""
                update res_project_budget_plan set synced = false
                where sync_budget_line_id in %s
            """, (tuple(self.ids),))
        return super(AccountBudgetLine, self).unlink()
