# -*- coding: utf-8 -*-
from openerp import models, fields


class ResFund(models.Model):
    _inherit = 'res.fund'

    unit_base = fields.Boolean(
        string='Unit Based',
        default=False
    )
    project_base = fields.Boolean(
        string='Project Based',
        default=False
    )
    personnel = fields.Boolean(
        string='Personnel',
        default=False
    )
    invest_asset = fields.Boolean(
        string='Investment Asset',
        default=False
    )
    invest_construction = fields.Boolean(
        string='Investment Construction',
        default=False
    )


class ResSection(models.Model):
    _inherit = 'res.section'

    fund_ids = fields.Many2many(
        domain="[('unit_base', '=', True)]",
    )


class ResProject(models.Model):
    _inherit = 'res.project'

    fund_ids = fields.Many2many(
        domain="[('project_base', '=', True)]",
    )


class ResPersonnelCostcenter(models.Model):
    _inherit = 'res.personnel.costcenter'

    fund_ids = fields.Many2many(
        domain="[('personnel', '=', True)]",
    )


class ResInvestConstruction(models.Model):
    _inherit = 'res.invest.construction'

    fund_ids = fields.Many2many(
        domain="[('invest_construction', '=', True)]",
    )


class ResInvestAsset(models.Model):
    _inherit = 'res.invest.asset'

    fund_ids = fields.Many2many(
        domain="[('invest_asset', '=', True)]",
    )
