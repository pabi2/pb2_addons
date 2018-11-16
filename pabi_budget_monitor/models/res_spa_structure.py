# -*- coding: utf-8 -*-
from openerp import fields, models


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
