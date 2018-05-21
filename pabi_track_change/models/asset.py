# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    code2 = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one('account.asset',
                                track_visibility='onchange')
    status = fields.Many2one('account.asset.status',
                             track_visibility='onchange')
    deliver_to = fields.Char(track_visibility='onchange')
    deliver_date = fields.Date(track_visibility='onchange')
    section_id = fields.Many2one('res.section',
                                 track_visibility='onchange')
    project_id = fields.Many2one('res.project',
                                 track_visibility='onchange')
    invest_asset_id = fields.Many2one('res.invest.asset',
                                      track_visibility='onchange')
    invest_construction_id = fields.Many2one('res.invest.construction',
                                             track_visibility='onchange')
    # profile_type = fields.Selection(track_visibility='onchange')
    method_time = fields.Selection(track_visibility='onchange')
    method_number = fields.Integer(track_visibility='onchange')
    method_period = fields.Selection(track_visibility='onchange')
    days_calc = fields.Boolean(track_visibility='onchange')
    method = fields.Selection(track_visibility='onchange')
    prorata = fields.Boolean(track_visibility='onchange')
    owner_section_id = fields.Many2one('res.section',
                                       track_visibility='onchange')
    owner_project_id = fields.Many2one('res.project',
                                       track_visibility='onchange')
    purchase_request_id = fields.Many2one('purchase.request',
                                          track_visibility='onchange')
    asset_purchase_method_id = fields.Many2one('asset.purchase.method',
                                               track_visibility='onchange')
    pr_requester_id = fields.Many2one('res.users',
                                      track_visibility='onchange')
    date_request = fields.Date(track_visibility='onchange')
    doc_request_id = fields.Many2one('account.asset.request',
                                     track_visibility='onchange')
    responsible_user_id = fields.Many2one('res.users',
                                          track_visibility='onchange')
    building_id = fields.Many2one('res.building',
                                  track_visibility='onchange')
    floor_id = fields.Many2one('res.floor',
                               track_visibility='onchange')
    room_id = fields.Many2one('res.room',
                              track_visibility='onchange')
    serial_number = fields.Char(track_visibility='onchange')
    warranty_start_date = fields.Date(track_visibility='onchange')
    warranty_expire_date = fields.Date(track_visibility='onchange')
    note = fields.Text(track_visibility='onchange')
