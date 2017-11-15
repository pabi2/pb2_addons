# -*- coding: utf-8 -*-

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pit_line = fields.One2many(
        'personal.income.tax',
        'partner_id',
        string='PIT',
        readonly=False,
    )
    pit_yearly = fields.One2many(
        'personal.income.tax.yearly',
        'partner_id',
        string='PIT Yearly',
        readonly=True,
    )
