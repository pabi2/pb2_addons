# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError


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
            raise UserError(_('Not a project based budget control'))
        # Find matched phases for this budget control
        Project = self.env['res.project']
        BudgetLine = self.env['account.budget.line']
        projects = Project.search([
            ('program_id', '=', self.program_id.id),
        ])
        # Clear budget_line without sync ref (myproject, we can't create here)
        prj_budget_lines = self.project_plan_ids.mapped('sync_budget_line_id')
        diff_lines = self.budget_line_ids - prj_budget_lines
        diff_lines.unlink()
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
                        'project_id': project.id,
                        'fund_id': (project.fund_ids and
                                    project.fund_ids[0].id or False),
                    }
                    budget_line = BudgetLine.create(budget_line_dict)
                    budget_line.update_related_dimension(budget_line_dict)
                    project_plan.sync_budget_line_id = budget_line
            project.sync_project_plan_to_budget_line([self.fiscalyear_id.id])
        return True
