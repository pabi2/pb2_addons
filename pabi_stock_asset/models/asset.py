# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockAsset(models.Model):

    _inherit = 'account.asset.asset'

    @api.onchange('section_id')
    def _onchange_section(self):
        self.org_id = self.section.org_id.id

    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    requester = fields.Many2one(
        'res.users',
        string='Requester',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Building',
    )
    room = fields.Char(
        string='Room',
    )
    serial_number = fields.Char(
        string='Serial Number',
    )
    warranty = fields.Integer(
        string='Warranty (Month)',
    )
    warranty_start_date = fields.Date(
        string='Warranty Start Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
    )
    warranty_expire_date = fields.Date(
        string='Warranty Expire Date',
        default=lambda self: fields.Date.context_today(self),
        track_visibility='onchange',
    )
