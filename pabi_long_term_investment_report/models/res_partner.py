# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    investment_ids = fields.One2many(
        'res.partner.investment',
        'partner_id',
        string='Long Term Investments',
    )
    percent_invest = fields.Float(
        string='Investment Percent',
    )


class ResPartnerInvestment(models.Model):
    _name = 'res.partner.investment'
    _description = 'Long term investment NSDTA made with this partner'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    name = fields.Char(
        string='Commitee Approval',
        required=True,
    )
    date_approve = fields.Date(
        string='Approved Date',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    total_captial = fields.Float(
        string='Registered Captial',
        required=True,
    )
    total_share = fields.Float(
        string='Number of Shares',
        required=True,
    )
    nstda_share = fields.Float(
        string='Number of Shares by NSTDA',
        required=True,
    )
    price_unit = fields.Float(
        string='Share Price',
        required=True,
    )
    price_subtotal = fields.Float(
        string='Amount',
        compute='_compute_price_subtotal',
        store=True,
    )
    move_line_ids = fields.One2many(
        'account.move.line',
        'investment_id',
        string='Invoice',
        domain=[('account_id.code', '=', '1203900001')],  # เงินลงทุนระยะยาว
    )

    @api.multi
    @api.depends('nstda_share', 'price_unit')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.nstda_share
