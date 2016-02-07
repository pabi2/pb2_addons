# -*- coding: utf-8 -*-
from openerp import models, fields


class res_partner(models.Model):

    _inherit = 'res.partner'

    property_retention_on_payment = fields.Boolean(
        string="Retention on Payment",
        company_dependent=True,
        readonly=False,
        help="""If this is checked, retention will be carried from invoice
                to payment for account posting. Otherwise on invoice.""")
    property_account_retention_customer = fields.Many2one(
        'account.account',
        string="Account Retention Customer",
        company_dependent=True,
        domain="[('type', '!=', 'view')]",
        required=False,
        readonly=True,
        help="""This account will be used instead of the default one
                as the retention account for the current partner""")
    property_account_retention_supplier = fields.Many2one(
        'account.account',
        string="Account Retention Supplier",
        company_dependent=True,
        domain="[('type', '!=', 'view')]",
        required=False,
        readonly=True,
        help="""This account will be used instead of the default one as the
                retention account for the current partner""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
