# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResOrg(models.Model):
    _inherit = 'res.org'

    monitor_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.org.monitor.view', 'org_id',
        string='Org Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_org(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_org_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResSector(models.Model):
    _inherit = 'res.sector'

    monitor_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.sector.monitor.view', 'sector_id',
        string='Sector Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_sector(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_sector_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResSubsector(models.Model):
    _inherit = 'res.subsector'

    monitor_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.subsector.monitor.view', 'subsector_id',
        string='Subsector Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_subsector(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_subsector_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResDivision(models.Model):
    _inherit = 'res.division'

    monitor_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.division.monitor.view', 'division_id',
        string='Division Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_division(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_division_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResSection(models.Model):
    _inherit = 'res.section'

    monitor_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.section.monitor.view', 'section_id',
        string='Section Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )
    job_order_ids = fields.Many2many(
        'cost.control',
        string='Job Order',
    )

    @api.multi
    def action_open_budget_monitor_section(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_section_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result


class ResCostcenter(models.Model):
    _inherit = 'res.costcenter'

    monitor_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.costcenter.monitor.view', 'costcenter_id',
        string='Costcenter Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )

    @api.multi
    def action_open_budget_monitor_costcenter(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_budget_monitor.action_budget_monitor_costcenter_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result
