# -*- coding: utf-8 -*-
from openerp import fields, models


class ResFund(models.Model):
    _inherit = 'res.fund'

    monitor_project_ids = fields.One2many(
        'res.fund.monitor.project.view', 'fund_id',
        string='Fund / Project Monitor',
    )
    monitor_section_ids = fields.One2many(
        'res.fund.monitor.section.view', 'fund_id',
        string='Fund / Section Monitor',
    )
    monitor_invest_asset_ids = fields.One2many(
        'res.fund.monitor.invest.asset.view', 'fund_id',
        string='Fund / Invest Asset Monitor',
    )
    monitor_invest_construction_phase_ids = fields.One2many(
        'res.fund.monitor.invest.construction.phase.view', 'fund_id',
        string='Fund / Invest Construction Phase Monitor',
    )
    monitor_personnel_costcenter_ids = fields.One2many(
        'res.fund.monitor.personnel.costcenter.view', 'fund_id',
        string='Fund / Personnel Budget Monitor',
    )
