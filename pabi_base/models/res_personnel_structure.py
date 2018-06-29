# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp.addons.pabi_base.models.res_common import ResCommon


# Personnel
class ResPersonnelCostcenter(ResCommon, models.Model):
    _name = 'res.personnel.costcenter'
    _description = 'Personnel Budget'
    _rescommon_name_search_list = ['org_id', 'sector_id',
                                   'subsector_id', 'division_id']

    division_id = fields.Many2one(
        'res.division',
        string='Division',
        required=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        required=True,
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        related='division_id.subsector_id',
        string='Subsector',
        readonly=True,
        store=True,
    )
    sector_id = fields.Many2one(
        'res.sector',
        related='division_id.sector_id',
        string='Sector',
        readonly=True,
        store=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='division_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        required=False,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_personnel_costcenter_rel',
        'personnel_costcenter_id', 'fund_id',
        string='Funds',
        default=lambda self: self.env.ref('base.fund_nstda'),
    )
