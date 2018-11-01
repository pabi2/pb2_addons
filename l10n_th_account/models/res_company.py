# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    retention_on_payment = fields.Boolean(
        string='Retention on Payment',
        default=False,
    )
    # Retention account setup
    account_retention_customer = fields.Many2one(
        'account.account',
        string='Account Retention Customer',
        domain=[('type', '!=', 'view')],
    )
    account_retention_supplier = fields.Many2one(
        'account.account',
        string='Account Retention Supplier',
        domain=[('type', '!=', 'view')],
    )
    account_retention_customer_ids = fields.Many2many(
        'account.account',
        'company_account_retention_customer_rel',
        'company_id', 'account_id',
        string='Account Retention Customer',
        domain=[('type', '!=', 'view')],
    )
    account_retention_supplier_ids = fields.Many2many(
        'account.account',
        'company_account_retention_supplier_rel',
        'company_id', 'account_id',
        string='Account Retention Supplier',
        domain=[('type', '!=', 'view')],
    )
    # --
    auto_recognize_vat = fields.Boolean(
        string='Auto recognize undue VAT on Supplier Payment',
        default=True,
    )
    recognize_vat_journal_id = fields.Many2one(
        'account.journal',
        string='Recognize VAT Journal',
        domain=[('type', '=', 'general')],
    )
