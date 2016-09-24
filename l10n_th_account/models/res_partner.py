# -*- coding: utf-8 -*-
from openerp import fields, models

INCOME_TAX_FORM = [('pnd3', 'PND3'), ('pnd53', 'PND53')]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        help="Default Income Tax Form for this Supplier in Supplier Payment",
    )
