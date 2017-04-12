# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.addons.pabi_base.models.res_common import ResCommon

CONSTRUCTION_PHASE = {
    '1-design': '1-Design',
    '2-control': '2-Control',
    '3-construct': '3-Construct',
    '4-procure': '4-Procurement',
    '5-other': '5-Others',
}


# Investment - Asset
class ResInvestAsset(ResCommon, models.Model):
    _name = 'res.invest.asset'
    _description = 'Investment Asset'

    invest_asset_categ_id = fields.Many2one(
        'res.invest.asset.category',
        string='Investment Asset Category'
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        required=True,
    )
    name_common = fields.Char(
        string='Common Name',
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_invest_asset_rel',
        'invest_asset_id', 'fund_id',
        string='Funds',
        default=lambda self: self.env.ref('base.fund_nstda'),
    )


class ResInvestAssetCategory(ResCommon, models.Model):
    _name = 'res.invest.asset.category'
    _description = 'Investment Asset Category'


# Investment - Construction
class ResInvestConstruction(ResCommon, models.Model):
    _name = 'res.invest.construction'
    _description = 'Investment Construction'

    phase_ids = fields.One2many(
        'res.invest.construction.phase',
        'invest_construction_id',
        string='Phases',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        required=True,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_invest_construction_rel',
        'invest_construction_id', 'fund_id',
        string='Funds',
        default=lambda self: self.env.ref('base.fund_nstda'),
    )


class ResInvestConstructionPhase(models.Model):
    _name = 'res.invest.construction.phase'
    _description = 'Investment Construction Phase'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Investment Construction',
        index=True,
        ondelete='cascade',
    )
    phase = fields.Selection(
        sorted(CONSTRUCTION_PHASE.items()),
        string='Phase',
        required=True,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        related='invest_construction_id.fund_ids',
        string='Funds',
    )
    _sql_constraints = [
        ('phase_uniq', 'unique(invest_construction_id, phase)',
            'Phase must be unique for a construction project!'),
    ]

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[%s] %s - %s" %
                           (rec.invest_construction_id.code,
                            rec.invest_construction_id.name,
                            CONSTRUCTION_PHASE[rec.phase])))
        return result
