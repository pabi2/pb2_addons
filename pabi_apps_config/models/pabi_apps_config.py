# -*- coding: utf-8 -*-
from openerp import fields, models, api


class PABIAppsConfigSettings(models.TransientModel):
    _name = 'pabi.apps.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    # res_partner_ext
    no_partner_tag_change_account = fields.Boolean(
        string="Disallow changing of Partner's Tag, "
               "when it result in changing account code for that partner",
        related="company_id.no_partner_tag_change_account",
    )
    default_employee_partner_categ_id = fields.Many2one(
        string="Default employee's partner category",
        related="company_id.default_employee_partner_categ_id",
        help="To be used when partner is auto created by creating new user"
    )
    # purchase_invoice_line_percentage
    account_deposit_supplier = fields.Many2one(
        'account.account',
        string='Supplier Advance Account',
        related="company_id.account_deposit_supplier",
    )
    # sale_invoice_line_percentage
    account_deposit_customer = fields.Many2one(
        'account.account',
        string='Customer Advance Account',
        related="company_id.account_deposit_customer",
    )
    # hr_expense_advance_clearing
    employee_advance_account_id = fields.Many2one(
        'account.account',
        string='Employee Advance Account',
        related="company_id.employee_advance_account_id",
    )
    # Other accounts for advance
    other_deposit_account_ids = fields.Many2many(
        'account.account',
        string='Other Advance Accounts',
        related="company_id.other_deposit_account_ids",
        help="Lst other eligible for user to choose manually on document",
    )
    # l10n_th_tax_detail
    account_tax_difference = fields.Many2one(
        'account.account',
        string='Tax Difference Account',
        related="company_id.account_tax_difference",
    )
    number_month_tax_addition = fields.Integer(
        string='Number of months for additional Tax',
        related="company_id.number_month_tax_addition",
    )
    # l10n_th_account
    retention_on_payment = fields.Boolean(
        string='Retention on Payment',
        related="company_id.retention_on_payment",
    )
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
    auto_recognize_vat = fields.Boolean(
        string='Auto recognize undue VAT on Supplier Payment',
        related="company_id.auto_recognize_vat",
    )
    recognize_vat_journal_id = fields.Many2one(
        'account.journal',
        string='Recognize VAT Journal',
        related="company_id.recognize_vat_journal_id",
    )
    # pabi_account
    tax_move_by_taxbranch = fields.Boolean(
        string="Tax Account Move by Tax Branch",
        related='company_id.tax_move_by_taxbranch',
    )
    wht_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string="Taxbranch for Withholding Tax",
        related='company_id.wht_taxbranch_id',
    )
    # pabi_purchase_work_acceptance
    delivery_penalty_activity_id = fields.Many2one(
        'account.activity',
        string='Delivery Penalty Activity',
        related="company_id.delivery_penalty_activity_id",
        domain="[('activity_group_ids', 'in',"
               "[delivery_penalty_activity_group_id or -1])]",
    )
    delivery_penalty_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Delivery Penalty Activity Group',
        related="company_id.delivery_penalty_activity_group_id",
    )
    # pabi_purchase_billing
    date_due_day = fields.Char(
        string="Due Date (Days)",
        help="Must be in 1,3, ... format.",
        default="16,28",
        related="company_id.date_due_day",
    )
    # pabi_ar_late_payment_penalty
    ar_late_payment_penalty_activity_id = fields.Many2one(
        'account.activity',
        string='AR Late payment Penalty Activity',
        related="company_id.ar_late_payment_penalty_activity_id",
        domain="[('activity_group_ids', 'in',"
               "[ar_late_payment_penalty_activity_group_id or -1])]",
    )
    ar_late_payment_penalty_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='AR Late payment Penalty Activity Group',
        related="company_id.ar_late_payment_penalty_activity_group_id",
    )
    # pabi_loan_receivable
    loan_penalty_product_id = fields.Many2one(
        'product.product',
        string='Loan Penalty Product',
        related="company_id.loan_penalty_product_id",
    )
    # pabi_advance_dunning_letter
    group_email = fields.Char(
        string='Group Email',
        related='company_id.group_email',
    )
    head_account_employee_id = fields.Many2one(
        'hr.employee',
        string='Head Accounting',
        related='company_id.head_account_employee_id',
    )
    # Loan Installment
    loan_installment_account_id = fields.Many2one(
        'account.account',
        string='Loan Installment Account',
        related="company_id.loan_installment_account_id",
    )
    loan_defer_income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        related="company_id.loan_defer_income_account_id",
    )
    loan_force_close_account_id = fields.Many2one(
        'account.account',
        string='Force Close Account',
        related="company_id.loan_force_close_account_id",
    )
    loan_income_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Income Activity Group',
        related="company_id.loan_income_activity_group_id",
    )
    loan_income_activity_id = fields.Many2one(
        'account.activity',
        string='Income Activity',
        related="company_id.loan_income_activity_id",
    )
    loan_income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        related="company_id.loan_income_account_id",
    )
    # Long term investment
    longterm_invest_account_id = fields.Many2one(
        'account.account',
        string='Long Term Investment Account',
        related="company_id.longterm_invest_account_id",
    )
    # Default AG for invest asset / construction
    default_ag_invest_asset_id = fields.Many2one(
        'account.activity.group',
        string='Default Invest Asset Activity Group',
        related="company_id.default_ag_invest_asset_id",
    )
    default_ag_invest_construction_id = fields.Many2one(
        'account.activity.group',
        string='Default Invest Construction Activity Group',
        related="company_id.default_ag_invest_construction_id",
    )

    @api.onchange('loan_income_activity_id')
    def _onchange_loan_income_activity_id(self):
        self.loan_income_account_id = self.loan_income_activity_id.account_id
