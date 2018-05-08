# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_company = fields.Boolean(
        track_visibility='onchange',
    )
    title = fields.Many2one(
        'res.partner.title',
        track_visibility='onchange',
    )
    parent_id = fields.Many2one(
        'res.partner',
        track_visibility='onchange',
    )
    category_id = fields.Many2one(
        'res.partner.category',
        track_visibility='onchange',
    )
    name = fields.Char(
        track_visibility='onchange',
    )
    vat = fields.Char(
        track_visibility='onchange',
    )
    taxbranch = fields.Char(
        track_visibility='onchange',
    )
    phone = fields.Char(
        track_visibility='onchange',
    )
    mobile = fields.Char(
        track_visibility='onchange',
    )
    fax = fields.Char(
        track_visibility='onchange',
    )
    email = fields.Char(
        track_visibility='onchange',
    )
    street = fields.Char(
        track_visibility='onchange',
    )
    country_id = fields.Many2one(
        'res.country',
        track_visibility='onchange',
    )
    province_id = fields.Many2one(
        'res.country.province',
        track_visibility='onchange',
    )
    district_id = fields.Many2one(
        'res.country.district',
        track_visibility='onchange',
    )
    township_id = fields.Many2one(
        'res.country.township',
        track_visibility='onchange',
    )
    zip = fields.Char(
        track_visibility='onchange',
    )
    street2 = fields.Char(
        track_visibility='onchange',
    )
    website = fields.Char(
        track_visibility='onchange',
    )
    comment = fields.Text(
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        'res.users',
        track_visibility='onchange',
    )
    ref = fields.Char(
        track_visibility='onchange',
    )
    date = fields.Date(
        track_visibility='onchange',
    )
    supplier = fields.Boolean(
        track_visibility='onchange',
    )
    customer = fields.Boolean(
        track_visibility='onchange',
    )
    active = fields.Boolean(
        track_visibility='onchange',
    )
    opt_out = fields.Boolean(
        track_visibility='onchange',
    )
    property_product_pricelist_purchase = fields.Many2one(
        'product.pricelist',
        track_visibility='onchange',
    )
    notify_email = fields.Selection(
        track_visibility='onchange',
    )
    property_account_position = fields.Many2one(
        'account.fiscal.position',
        track_visibility='onchange',
    )
    # property_purchase_position = fields.Many2one(
    #     track_visibility='onchange',
    # )
    property_account_receivable = fields.Many2one(
        'account.account',
        track_visibility='onchange',
    )
    property_account_payable = fields.Many2one(
        'account.account',
        track_visibility='onchange',
    )
    last_reconcilation_date = fields.Date(
        track_visibility='onchange',
    )
    property_payment_term = fields.Many2one(
        'account.payment.term',
        track_visibility='onchange',
    )
    property_supplier_payment_term = fields.Many2one(
        'account.payment.term',
        track_visibility='onchange',
    )
    supplier_invoice_method = fields.Selection(
        track_visibility='onchange',
    )
    credit_limit = fields.Float(
        track_visibility='onchange',
    )
    income_tax_form = fields.Selection(
        track_visibility='onchange',
    )
