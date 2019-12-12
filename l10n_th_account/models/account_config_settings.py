# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    retention_on_payment = fields.Boolean(
        string='Retention on Payment',
        related="company_id.retention_on_payment",
    )
    # Retention (will be changed to multi values)
    account_retention_customer = fields.Many2one(
        'account.account',
        string='Account Retention Customer',
        related="company_id.account_retention_customer",
    )
    account_retention_supplier = fields.Many2one(
        'account.account',
        string='Account Retention Supplier',
        related="company_id.account_retention_supplier",
    )
    account_retention_customer_ids = fields.Many2many(
        'account.account',
        string='Account Retention Customer',
        related="company_id.account_retention_customer_ids",
    )
    account_retention_supplier_ids = fields.Many2many(
        'account.account',
        string='Account Retention Supplier',
        related="company_id.account_retention_supplier_ids",
    )
    # --
    auto_recognize_vat = fields.Boolean(
        string='Auto recognize undue VAT on Supplier Payment',
        related="company_id.auto_recognize_vat",
    )
    recognize_vat_journal_id = fields.Many2one(
        'account.journal',
        string='Recognize VAT Journal',
        related="company_id.recognize_vat_journal_id",
    )
    group_email_wht = fields.Char(
        string='Group Email WHT',
        related='company_id.group_email_wht',
    )
