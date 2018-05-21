# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


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

    @api.multi
    @api.constrains('investment_ids')
    def _check_investment_invoice_ids(self):
        invoice_ids = []
        for rec in self:
            for invest in rec.investment_ids:
                invoice_ids += invest.invoice_ids.ids
        if len(invoice_ids) != len(list(set(invoice_ids))):
            raise ValidationError(
                _('One invoice can relate to only one investment'))


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
    total_capital = fields.Float(
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
    invoice_ids = fields.Many2many(
        'account.invoice',
        'partner_investment_invoice_rel',
        'investment_id', 'invoice_id',
        string='Invoices',
        domain=lambda self: self._get_domain_invoices(),
    )
    move_line_ids = fields.One2many(
        'account.move.line',
        'investment_id',
        string='Invoice',
        compute='_compute_move_line_ids',
        store=True,
    )

    @api.model
    def _get_domain_invoices(self):
        account = self.env.user.company_id.longterm_invest_account_id
        dom = """
            [('state', 'in', ('open', 'paid')),
             ('partner_id', '=', partner_id),
             ('invoice_line.account_id', '=', %s)]
        """ % account.id
        return dom

    @api.multi
    @api.depends('invoice_ids')
    def _compute_move_line_ids(self):
        for rec in self:
            # get only long term investment account
            account = self.env.user.company_id.longterm_invest_account_id
            move_lines = rec.invoice_ids.mapped('move_id.line_id').\
                filtered(lambda l: l.account_id == account)
            rec.move_line_ids = move_lines

    @api.multi
    @api.depends('nstda_share', 'price_unit')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.nstda_share
