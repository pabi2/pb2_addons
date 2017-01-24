# -*- coding: utf-8 -*-

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pit_line = fields.One2many(
        'personal.income.tax',
        'partner_id',
        string='Tax Line PIT',
        readonly=True,
    )
