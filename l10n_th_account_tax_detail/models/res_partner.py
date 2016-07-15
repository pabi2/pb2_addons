# -*- coding: utf-8 -*-

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_tax_difference = fields.Many2one(
        'account.account',
        string="Account Tax Difference",
        company_dependent=True,
        domain="[('type', '!=', 'view')]",
        required=True,
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
