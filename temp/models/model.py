# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class XXX(models.TransientModel):
    _name = "invest.asset.selection.wiz"

    invset_asset_wiz_line_ids = fields.One2many(
        'invest.asset.selection.wiz.line',
        'wiz_id',
        string='Lines',
    )


class YYY(models.TransientModel):
    _name = "invest.asset.selection.wiz.line"

    wiz_id = fields.Many2one(
        'invest.asset.selection.wiz.line',
        string='Wizard',
    )


class ZZZ(models.TransientModel):
    _name = "search.partner.dunning.report.wizard"
