# -*- coding: utf-8 -*-

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_tax_move_by_taxbranch = fields.Boolean(
        string="Tax Account Move by Tax Branch",
        company_dependent=True,
        readonly=True,
    )
    property_wht_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string="Taxbranch for Withholding Tax",
        company_dependent=True,
        required=True,
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
