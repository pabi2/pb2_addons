# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResSpa(models.Model):
    _inherit = 'res.spa'

    monitor_ids = fields.One2many(
        'res.spa.monitor.view', 'spa_id',
        string='SPA Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.spa.monitor.view', 'spa_id',
        string='SPA Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.spa.monitor.view', 'spa_id',
        string='SPA Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResMission(models.Model):
    _inherit = 'res.mission'

    monitor_ids = fields.One2many(
        'res.mission.monitor.view', 'mission_id',
        string='Mission Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.mission.monitor.view', 'mission_id',
        string='Mission Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.mission.monitor.view', 'mission_id',
        string='Mission Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResTagType(models.Model):
    _inherit = 'res.tag.type'

    monitor_ids = fields.One2many(
        'res.tag.type.monitor.view', 'tag_type_id',
        string='Tag Type Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.tag.type.monitor.view', 'tag_type_id',
        string='Tag Type Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.tag.type.monitor.view', 'tag_type_id',
        string='Tag Type Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResTag(models.Model):
    _inherit = 'res.tag'

    monitor_ids = fields.One2many(
        'res.tag.monitor.view', 'tag_id',
        string='Tag Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.tag.monitor.view', 'tag_id',
        string='Tag Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.tag.monitor.view', 'tag_id',
        string='Tag Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResFunctionalArea(models.Model):
    _inherit = 'res.functional.area'

    monitor_ids = fields.One2many(
        'res.functional.area.monitor.view', 'functional_area_id',
        string='Functional Area Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.functional.area.monitor.view', 'functional_area_id',
        string='Functional Area Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,

    )
    monitor_expense_ids = fields.One2many(
        'res.functional.area.monitor.view', 'functional_area_id',
        string='Functional Area Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_functional(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_functional_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResProgramGroup(models.Model):
    _inherit = 'res.program.group'

    monitor_ids = fields.One2many(
        'res.program.group.monitor.view', 'program_group_id',
        string='Program Group Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.program.group.monitor.view', 'program_group_id',
        string='Program Group Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.program.group.monitor.view', 'program_group_id',
        string='Program Group Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_program_group(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_program_group_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResProgram(models.Model):
    _inherit = 'res.program'

    monitor_ids = fields.One2many(
        'res.program.monitor.view', 'program_id',
        string='Program Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.program.monitor.view', 'program_id',
        string='Program Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.program.monitor.view', 'program_id',
        string='Program Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_program(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_program_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResProjectGroup(models.Model):
    _inherit = 'res.project.group'

    monitor_ids = fields.One2many(
        'res.project.group.monitor.view', 'project_group_id',
        string='Project Group Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.project.group.monitor.view', 'project_group_id',
        string='Project Group Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.project.group.monitor.view', 'project_group_id',
        string='Project Group Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_project_group(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_project_group_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResProject(models.Model):
    _inherit = 'res.project'

    monitor_ids = fields.One2many(
        'res.project.monitor.view', 'project_id',
        string='Project Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.project.monitor.view', 'project_id',
        string='Project Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.project.monitor.view', 'project_id',
        string='Project Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )
    monitor_revenue_view_ids = fields.One2many(
        'res.project.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Project Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )
    monitor_expense_view_ids = fields.One2many(
        'res.project.monitor.only.view',
        compute='_compute_budget_monitor',
        readonly=True,
        string='Project Monitor',
        help='This field created for speed performance views \
        in Budget Monitor Tab only',
    )

    @api.multi
    def _compute_budget_monitor(self):
        self.ensure_one()
        # create new project not query
        if not isinstance(self.id, int):
            return True
        # delete all record and create new for performance on menu myProject
        self._cr.execute("""delete from res_project_monitor_only_view""")
        self._cr.execute("""
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id) AS id,
                budget_method, charge_type, fiscalyear_id,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) +
                COALESCE(sum(amount_pr_commit),0) +
                COALESCE(sum(amount_po_commit),0) +
                COALESCE(sum(amount_exp_commit),0) +
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) -
                COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where project_id = %s
            group by budget_method, charge_type, fiscalyear_id
        """ % (self.id, ))
        results = self._cr.dictfetchall()
        ReportLine = self.env['res.project.monitor.only.view']
        for line in results:
            if line.get('budget_method') == 'expense':
                self.monitor_expense_view_ids += ReportLine.create(line)
            if line.get('budget_method') == 'revenue':
                self.monitor_revenue_view_ids += ReportLine.create(line)
        return True


class ResProjectMonitorViewOnly(models.TransientModel):
    _name = 'res.project.monitor.only.view'
    _inherit = 'monitor.view'
