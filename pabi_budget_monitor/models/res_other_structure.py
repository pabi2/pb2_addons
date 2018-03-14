# -*- coding: utf-8 -*-
from openerp import fields, models


class CostControl(models.Model):
    _inherit = 'cost.control'

    monitor_ids = fields.One2many(
        'res.cost.control.monitor.view', 'cost_control_id',
        string='Job Order Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.cost.control.monitor.view', 'cost_control_id',
        string='Controlenter Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.cost.control.monitor.view', 'cost_control_id',
        string='Job Order Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class CostControlType(models.Model):
    _inherit = 'cost.control.type'

    monitor_ids = fields.One2many(
        'res.cost.control.type.monitor.view', 'cost_control_type_id',
        string='Job Order Type Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.cost.control.type.monitor.view', 'cost_control_type_id',
        string='Job Order Type Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.cost.control.type.monitor.view', 'cost_control_type_id',
        string='Job Order Type Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResPersonnelCostcenter(models.Model):
    _inherit = 'res.personnel.costcenter'

    monitor_ids = fields.One2many(
        'res.personnel.costcenter.monitor.view', 'personnel_costcenter_id',
        string='Personnel Budget Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.personnel.costcenter.monitor.view', 'personnel_costcenter_id',
        string='Personnel Budget Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.personnel.costcenter.monitor.view', 'personnel_costcenter_id',
        string='Personnel Budget Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResInvestAsset(models.Model):
    _inherit = 'res.invest.asset'

    monitor_ids = fields.One2many(
        'res.invest.asset.monitor.view', 'invest_asset_id',
        string='Investment Asset Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.invest.asset.monitor.view', 'invest_asset_id',
        string='Investment Asset Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.invest.asset.monitor.view', 'invest_asset_id',
        string='Investment Asset Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResInvestConstruction(models.Model):
    _inherit = 'res.invest.construction'

    monitor_ids = fields.One2many(
        'res.invest.construction.monitor.view', 'invest_construction_id',
        string='Investment Construction Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.invest.construction.monitor.view', 'invest_construction_id',
        string='Investment Construction Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.invest.construction.monitor.view', 'invest_construction_id',
        string='Investment Construction Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )


class ResInvestConstructionPhase(models.Model):
    _inherit = 'res.invest.construction.phase'

    monitor_ids = fields.One2many(
        'res.invest.construction.phase.monitor.view',
        'invest_construction_phase_id',
        string='Investment Construction Phase Monitor',
        readonly=True,
    )
    monitor_revenue_ids = fields.One2many(
        'res.invest.construction.phase.monitor.view',
        'invest_construction_phase_id',
        string='Investment Construction Phase Monitor',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    monitor_expense_ids = fields.One2many(
        'res.invest.construction.phase.monitor.view',
        'invest_construction_phase_id',
        string='Investment Construction Phase Monitor',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )
