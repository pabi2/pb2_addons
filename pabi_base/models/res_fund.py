# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp.addons.pabi_base.models.res_common import ResCommon


class ResFund(ResCommon, models.Model):
    _name = 'res.fund'
    _description = 'Fund'

    type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Type',
        required=True,
    )
    project_ids = fields.Many2many(
        'res.project',
        'res_fund_project_rel',
        'fund_id', 'project_id',
        string='Projects',
    )
    section_ids = fields.Many2many(
        'res.section',
        'res_fund_section_rel',
        'fund_id', 'section_id',
        string='Sections',
    )
    invest_asset_ids = fields.Many2many(
        'res.invest.asset',
        'res_fund_invest_asset_rel',
        'fund_id', 'invest_asset_id',
        string='Investment Assets',
    )
    invest_construction_phase_ids = fields.Many2many(
        'res.invest.construction.phase',
        'res_fund_invest_construction_phase_rel',
        'fund_id', 'invest_construction_phase_id',
        string='Investment Construction Phases',
    )
    personnel_costcenter_ids = fields.Many2many(
        'res.personnel.costcenter',
        'res_fund_personnel_costcenter_rel',
        'fund_id', 'personnel_costcenter_id',
        string='Personnel Costcenters',
    )
