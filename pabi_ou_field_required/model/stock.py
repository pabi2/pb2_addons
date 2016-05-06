# -*- coding: utf-8 -*-
from openerp import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    operating_unit_id = fields.Many2one(required=True)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    operating_unit_id = fields.Many2one(required=True)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operating_unit_id = fields.Many2one(required=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    operating_unit_id = fields.Many2one(required=True)
    operating_unit_dest_id = fields.Many2one(required=True)
