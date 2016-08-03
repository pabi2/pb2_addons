# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class PaymentExportConfigLine(models.Model):
    _name = 'payment.export.config.lines'
    _description = 'Payment Export Configuration Lines'

    @api.constrains('sequence', 'length')
    def _check_sequence(self):
        for line in self:
            if line.sequence <= 0:
                raise UserError(_('Sequence must be greater then zero.'))
            if line.length <= 0:
                raise UserError(_('Length must be greater then zero.'))

    header_configure_id = fields.Many2one(
        'payment.export.config',
        string='Header Configuration',
    )
    footer_configure_id = fields.Many2one(
        'payment.export.config',
        string='Footer Configuration',
    )
    invoice_configure_id = fields.Many2one(
        'payment.export.config',
        string='Invoice Detail Configuration',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
    )
    field_code = fields.Text(
        string='Field Code',
        required=False,
    )
    length = fields.Integer(
        string='Length',
        required=True,
    )
    mandatory = fields.Boolean(
        string='Mandatory?',
    )
    notes = fields.Text(
        string='Remarks',
    )


class PaymentExportConfig(models.Model):
    _name = 'payment.export.config'
    _description = 'Payment Export Configuration'

    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.today(),
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        required=False,
        default = lambda self:self.env.uid,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=False,
        default=lambda self: self.env['res.company']._company_default_get('payment.export.config'),
    )
    header_config_line_ids = fields.One2many(
        'payment.export.config.lines',
        'header_configure_id',
        string='Header Configurations',
    )
    footer_config_line_ids = fields.One2many(
        'payment.export.config.lines',
        'footer_configure_id',
        string='Footer Configurations',
    )
    invoice_config_line_ids = fields.One2many(
        'payment.export.config.lines',
        'invoice_configure_id',
        string='Invoice Configurations',
    )
