# -*- coding: utf-8 -*-
from openerp import fields, models


class CostControl(models.Model):
    _inherit = 'cost.control'

    monitor_ids = fields.One2many(
        'res.cost.control.monitor.view', 'cost_control_id',
        string='Cost Control Monitor',
    )


class CostControlType(models.Model):
    _inherit = 'cost.control.type'

    monitor_ids = fields.One2many(
        'res.cost.control.type.monitor.view', 'cost_control_type_id',
        string='Cost Control Type Monitor',
    )


class ResPersonnelCostcenter(models.Model):
    _inherit = 'res.personnel.costcenter'

    monitor_ids = fields.One2many(
        'res.personnel.costcenter.monitor.view', 'personnel_costcenter_id',
        string='Personnel Budget Monitor',
    )


class ResInvestAsset(models.Model):
    _inherit = 'res.invest.asset'

    monitor_ids = fields.One2many(
        'res.invest.asset.monitor.view', 'invest_asset_id',
        string='Investment Asset Monitor',
    )


class ResInvestConstruction(models.Model):
    _inherit = 'res.invest.construction'

    monitor_ids = fields.One2many(
        'res.invest.construction.monitor.view', 'invest_construction_id',
        string='Investment Construction Monitor',
    )
