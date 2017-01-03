# -*- coding: utf-8 -*-
from openerp import models, fields


class StockRequest(models.Model):

    _inherit = 'stock.request'

    name = fields.Char(
        track_visibility='onchange',
    )
    company_id = fields.Many2one(
        track_visibility='onchange',
    )
    type = fields.Selection(
        track_visibility='onchange',
    )
    employee_id = fields.Many2one(
        track_visibility='onchange',
    )
    prepare_emp_id = fields.Many2one(
        track_visibility='onchange',
    )
    receive_emp_id = fields.Many2one(
        track_visibility='onchange',
    )
    picking_type_id = fields.Many2one(
        track_visibility='onchange',
    )
    location_id = fields.Many2one(
        track_visibility='onchange',
    )
    location_dest_id = fields.Many2one(
        track_visibility='onchange',
    )
    location_borrow_id = fields.Many2one(
        track_visibility='onchange',
    )
    transfer_picking_id = fields.Many2one(
        track_visibility='onchange',
    )
    return_picking_id = fields.Many2one(
        track_visibility='onchange',
    )
    line_ids = fields.One2many(
        track_visibility='onchange',
    )
    line2_ids = fields.One2many(
        track_visibility='onchange',
    )
    note = fields.Text(
        track_visibility='onchange',
    )
