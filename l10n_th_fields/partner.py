# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(string='Tax ID', size=13)
    taxbranch = fields.Char(string='Tax Branch ID', size=5)

    @api.one
    @api.constrains('vat')
    def _check_vat(self):
        if self.vat and len(self.vat) != 13:
            raise ValidationError(
                _("Tax ID must be 13 digits!"))

    @api.one
    @api.constrains('taxbranch')
    def _check_taxbranch(self):
        if self.taxbranch and len(self.taxbranch) != 5:
            raise ValidationError(
                _("Tax Branch must be 5 digits"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
