# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.addons.pabi_base.models.res_common import ResCommon


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


class ResInvestConstructionPhase(models.Model):
    _name = 'res.invest.construction.phase'
    _description = 'Investment Construction Phase'
    _order = 'sequence, id'

    PHASE = {'design': 'Design',
             'control': 'Control',
             'construct': 'Construct',
             'procure': 'Procurement',
             'other': 'Others'}

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Investment Construction',
        required=True,
    )
    phase = fields.Selection(
        PHASE.items(),
        string='Phase',
        required=True,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_invest_construction_phase_rel',
        'invest_construction_phase_id', 'fund_id',
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
            result.append((rec.id, "%s - %s" %
                           (rec.invest_construction_id.name_get(),
                            self.PHASE[rec.phase])))
        return result
