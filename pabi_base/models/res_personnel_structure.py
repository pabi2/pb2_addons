# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp.addons.pabi_base.models.res_common import ResCommon


# Personnel
class ResPersonnelCostcenter(ResCommon, models.Model):
    _name = 'res.personnel.costcenter'
    _description = 'Personnel Budget'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_personnel_costcenter_rel',
        'personnel_costcenter_id', 'fund_id',
        string='Funds',
        default=lambda self: self.env.ref('base.fund_nstda'),
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        required=True,
    )
