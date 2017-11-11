# -*- coding: utf-8 -*-
from openerp import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class StockLocation(models.Model):
    _inherit = 'stock.location'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,  # Set to false temp, due to error on PO approve.
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class StockMove(models.Model):
    _inherit = 'stock.move'

    operating_unit_id = fields.Many2one(required=False)
    operating_unit_dest_id = fields.Many2one(required=False)
