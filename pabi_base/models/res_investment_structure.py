# -*- coding: utf-8 -*-
from openerp import fields, models, api


# Investment - Asset
class ResInvestAsset(models.Model):
    _name = 'res.invest.asset'
    _description = 'Investment Asset'

    name = fields.Char(
        string='Name',
        required=True,
    )
    invest_asset_categ_id = fields.Many2one(
        'res.invest.asset.category',
        string='Investment Asset Category'
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )


class ResInvestAssetCategory(models.Model):
    _name = 'res.invest.asset.category'
    _description = 'Investment Asset Category'

    name = fields.Char(
        string='Name',
        required=True,
    )


# Investment - Construction
class ResInvestConstruction(models.Model):
    _name = 'res.invest.construction'
    _description = 'Investment Construction'

    name = fields.Char(
        string='Name',
        required=True,
    )
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
    _sql_constraints = [
        ('phase_uniq', 'unique(invest_construction_id, phase)',
            'Phase must be unique for a construction project!'),
    ]

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s - %s" %
                           (rec.invest_construction_id.name,
                            self.PHASE[rec.phase])))
        return result
