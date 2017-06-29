# -*- coding: utf-8 -*-
from openerp import fields, models


class ResOrg(models.Model):
    _inherit = 'res.org'

    monitor_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
    )
    monitor_revenue_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
        domain=[('budget_method', '=', 'revenue')],
    )
    monitor_expense_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
        domain=[('budget_method', '=', 'expense')],
    )


class ResSector(models.Model):
    _inherit = 'res.sector'

    monitor_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
    )
    monitor_revenue_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
        domain=[('budget_method', '=', 'revenue')],
    )
    monitor_expense_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
        domain=[('budget_method', '=', 'expense')],
    )


class ResSubsector(models.Model):
    _inherit = 'res.subsector'

    monitor_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
    )
    monitor_revenue_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
        domain=[('budget_method', '=', 'revenue')],
    )
    monitor_expense_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
        domain=[('budget_method', '=', 'expense')],
    )


class ResDivision(models.Model):
    _inherit = 'res.division'

    monitor_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
    )
    monitor_revenue_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
        domain=[('budget_method', '=', 'revenue')],
    )
    monitor_expense_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
        domain=[('budget_method', '=', 'expense')],
    )


class ResSection(models.Model):
    _inherit = 'res.section'

    monitor_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
    )
    monitor_revenue_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
        domain=[('budget_method', '=', 'revenue')],
    )
    monitor_expense_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
        domain=[('budget_method', '=', 'expense')],
    )
    program_rpt_id = fields.Many2one(
        'res.program',
        string='Report Program',
    )


class ResCostcenter(models.Model):
    _inherit = 'res.costcenter'

    monitor_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
    )
    monitor_revenue_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
        domain=[('budget_method', '=', 'revenue')],
    )
    monitor_expense_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
        domain=[('budget_method', '=', 'expense')],
    )
