# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockRequest(models.Model):
    _inherit = 'stock.request'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
