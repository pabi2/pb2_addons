# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, tools, _
from openerp.addons.pabi_account_move_document_ref.models.account_move import \
    DOCTYPE_SELECT
from openerp.exceptions import ValidationError
import time

PREFIX_DOCTYPE = {
    'incoming_shipment': 'IN',
    'delivery_order': 'OUT',
    'internal_transfer': 'INT',
    'bank_receipt': 'RV',
    'out_invoice': 'DV',
    'out_refund': 'CN',
    'out_invoice_debitnote': 'DN',
    'in_invoice': 'KV',
    'in_refund': 'SN',
    'in_invoice_debitnote': 'SDN',
    'receipt': 'RC',
    'payment': 'PV',
    'employee_expense': 'EX',
    'salary_expense': 'SLR',
    'interface_account': 'IA',
    # For analytic line only (budget commitment)
    'purchase_request': 'PR',
    'purchase_order': 'PO',
    'sale_order': 'SO',
    # Non document related, adjustment
    'adjustment': 'JN',
    # Special Type for Monitoring Report
    'account_budget': False,
}

REFERENCE_SELECT = [
    ('res.section', 'Section'),
    ('res.project', 'Project'),
    ('res.personnal.costcenter', 'Personnal Costcenter'),
    ('res.invest.asset', 'Invest Asset'),
    ('res.invest.construction', 'Invest Construction'),
]


class ReportAccountCommon(models.AbstractModel):
    _name = 'report.account.common'
    _inherit = 'xlsx.report'

    chart_account_id = fields.Many2one(
        'account.account',
        string='Chart of Accounts',
        domain=[('parent_id', '=', False)],
        required=True,
        default=lambda self: self._get_account(),
        help='Select Chart of Accounts',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    fiscalyear_start_id = fields.Many2one(
        'account.fiscalyear',
        string='Start Fiscal Year',
        default=lambda self: self._get_fiscalyear(),
    )
    fiscalyear_end_id = fields.Many2one(
        'account.fiscalyear',
        string='End Fiscal Year',
        default=lambda self: self._get_fiscalyear(),
    )
    fiscalyear_date_start = fields.Date(
        string='Start Fiscal Year Date',
        compute='_compute_fiscalyear_date',
    )
    fiscalyear_date_end = fields.Date(
        string='End Fiscal Year Date',
        compute='_compute_fiscalyear_date',
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_date', 'Dates'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_no',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    period_start_id = fields.Many2one(
        'account.period',
        string='Start Period',
    )
    period_end_id = fields.Many2one(
        'account.period',
        string='End Period',
    )

    @api.model
    def _get_account(self):
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('parent_id', '=', False)]
        account = self.env['account.account'].search(domain, limit=1)
        return account

    @api.model
    def _get_fiscalyear(self):
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', self.env.user.company_id.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        return fiscalyear

    @api.multi
    @api.depends('fiscalyear_start_id', 'fiscalyear_end_id')
    def _compute_fiscalyear_date(self):
        # For filter period by fiscalyear
        self.ensure_one()
        Fiscalyear = self.env['account.fiscalyear']
        date_start = self.fiscalyear_start_id.date_start
        date_end = self.fiscalyear_end_id.date_stop
        if date_start or date_end:
            domain = [('company_id', '=', self.company_id.id)]
            if not date_start:
                fiscalyear = Fiscalyear.search(
                    domain, order="date_start", limit=1)
                date_start = fiscalyear.date_start
            if not date_end:
                fiscalyear = Fiscalyear.search(
                    domain, order="date_stop desc", limit=1)
                date_end = fiscalyear.date_stop
        self.fiscalyear_date_start = date_start
        self.fiscalyear_date_end = date_end

    @api.onchange('chart_account_id')
    def _onchange_chart_account_id(self):
        if not self.chart_account_id:
            return {}
        # --
        company = self.chart_account_id.company_id
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', company.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        self.company_id = company
        self.fiscalyear_start_id = fiscalyear
        self.fiscalyear_end_id = fiscalyear
        if self.filter == "filter_period":
            Period = self.env['account.period']
            period_start = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 # ('special', '=', False)
                 ], order="code", limit=1)
            period_end = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 ('date_start', '<=', now), ('date_stop', '>=', now),
                 # ('special', '=', False)
                 ], limit=1)
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = fiscalyear.date_start
            self.date_end = fiscalyear and now or False

    @api.multi
    def _get_common_period_and_date(self):
        self.ensure_one()
        period_start = period_end = False
        date_start = date_end = False
        now = time.strftime('%Y-%m-%d')
        fiscalyear_date_start = self.fiscalyear_date_start
        fiscalyear_date_end = self.fiscalyear_date_end
        Period = self.env['account.period'].with_context(
            company_id=self.company_id.id)
        if fiscalyear_date_start and fiscalyear_date_end and \
           fiscalyear_date_end >= fiscalyear_date_start:
            ctx = {'account_period_prefer_normal': False}
            if now >= fiscalyear_date_start and now <= fiscalyear_date_end:
                period_start = \
                    Period.with_context(ctx).find(dt=fiscalyear_date_start) \
                    .sorted(key=lambda l: l.code)[0]
                period_end = Period.find(dt=now)[0]
                date_start = fiscalyear_date_start
                date_end = now
            elif fiscalyear_date_end < now:
                period_start = \
                    Period.with_context(ctx).find(dt=fiscalyear_date_start) \
                    .sorted(key=lambda l: l.code)[0]
                period_end = Period.find(dt=fiscalyear_date_end)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_end
            elif fiscalyear_date_start > now:
                period_start = \
                    Period.with_context(ctx).find(dt=fiscalyear_date_start) \
                    .sorted(key=lambda l: l.code)[0]
                period_end = Period.find(dt=fiscalyear_date_start)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_start
        return period_start, period_end, date_start, date_end

    @api.onchange('fiscalyear_start_id', 'fiscalyear_end_id')
    def _onchange_fiscalyear_id(self):
        period_start, period_end, date_start, date_end = \
            self._get_common_period_and_date()
        if self.filter == "filter_period":
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = date_start
            self.date_end = date_end

    @api.onchange('filter')
    def _onchange_filter(self):
        period_start, period_end, date_start, date_end = \
            self._get_common_period_and_date()
        self.period_start_id = self.period_end_id = False
        self.date_start = self.date_end = False
        if self.filter == "filter_period":
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = date_start
            self.date_end = date_end

    @api.multi
    def run_report(self):
        raise ValidationError(_('Not implemented.'))


# class FieldReportAccountMove(object):
#     # For Report Only
#     prefix_doctype = fields.Char(
#         string='Prefix Document Type',
#         compute='_compute_prefix_doctype',
#     )
#
#     @api.multi
#     def _compute_prefix_doctype(self):
#         for rec in self:
#             rec.prefix_doctype = PREFIX_DOCTYPE.get(rec.doctype, False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # For report only
    prefix_doctype = fields.Char(
        string='Prefix Document Type',
        compute='_compute_prefix_doctype',
    )

    @api.multi
    def _compute_prefix_doctype(self):
        for rec in self:
            prefix_doctype = rec.name[0:3]
            if prefix_doctype[-1] in ['0', '1', '2', '3', '4', '5', '6', '7',
                                      '8', '9', '/', '.', '-']:
                prefix_doctype = rec.name[0:2]
            rec.prefix_doctype = prefix_doctype


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # For report only
    prefix_doctype = fields.Char(
        string='Prefix Document Type',
        compute='_compute_prefix_doctype',
    )

    @api.multi
    def _compute_prefix_doctype(self):
        for rec in self:
            prefix_doctype = rec.move_id.name[0:3]
            if prefix_doctype[-1] in ['0', '1', '2', '3', '4', '5', '6', '7',
                                      '8', '9', '/', '.', '-']:
                prefix_doctype = rec.move_id.name[0:2]
            rec.prefix_doctype = prefix_doctype


class PabiCommonAccountReportView(models.Model):
    _name = 'pabi.common.account.report.view'
    _auto = False

    # Invoice
    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    invoice_move_id = fields.Many2one(
        'account.move',
        string='Move',
        readonly=True,
    )
    invoice_document_date = fields.Date(
        string='Invoice Document Date',
        readonly=True,
    )
    invoice_posting_date = fields.Date(
        string='Invoice Posting Date',
        readonly=True,
    )
    document_number = fields.Char(
        string='Document Number',
        readonly=True,
    )
    supplier_invoice_number = fields.Char(
        string='Supplier Invoice Number',
        readonly=True,
    )
    purchase_billing_id = fields.Many2one(
        'purchase.billing',
        string='Purchase Billing',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        readonly=True,
    )
    date_due_invoice = fields.Date(
        string='Invoice Due Date',
        readonly=True,
    )
    invoice_state = fields.Selection(
        [('draft', 'Draft'),
         ('proforma', 'Pro-forma'),
         ('proforma2', 'Pro-forma'),
         ('open', 'Open'),
         ('paid', 'Paid'),
         ('cancel', 'Cancelled')],
        string='Invoice State',
        readonly=True,
    )
    source_document_id = fields.Reference(
        [('purchase.order', 'Purchase'),
         ('sale.order', 'Sales'),
         ('hr.expense.expense', 'HR Expense')],
        string='Source Document Ref.',
        readonly=True,
    )
    amount_untaxed = fields.Float(
        string='Subtotal',
        readonly=True,
    )
    invoice_move_line_id = fields.Many2one(
        'account.move.line',
        string='Invoice Move Line',
        readonly=True,
    )
    amount_tax = fields.Float(
        string='Tax',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
    )
    invoice_narration = fields.Char(
        string='Invoice Narration',
        readonly=True,
    )
    invoice_move_write_uid = fields.Many2one(
        'res.users',
        string='Invoice Move Write',
        readonly=True,
    )
    invoice_move_validate_user_id = fields.Many2one(
        'res.users',
        related='invoice_move_id.validate_user_id',
        string='Validated By',
    )
    system_id = fields.Many2one(
        'interface.system',
        string='System Origin',
        readonly=True,
    )
    document_origin = fields.Char(
        string='Document Origin',
        readonly=True,
    )
    reconcile_id = fields.Many2one(
        'account.move.reconcile',
        string='Reconcile',
        readonly=True,
    )
    budget = fields.Reference(
        REFERENCE_SELECT,
        string='Budget',
        readonly=True,
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )
    move_line_name = fields.Char(
        string='Description',
        readonly=True,
    )
    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        readonly=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        readonly=True,
    )
    docline_seq = fields.Integer(
        string='#',
        readonly=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        readonly=True,
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Job Order Type',
        readonly=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        readonly=True,
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        readonly=True,
    )
    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
    )
    payment_term = fields.Many2one(
        'account.payment.term',
        string='Payment Terms',
        readonly=True,
    )
    # Voucher
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
    )
    voucher_move_line_id = fields.Many2one(
        'account.move.line',
        string='Voucher Move Line',
        readonly=True,
    )
    transfer_type = fields.Selection(
        [('direct', 'DIRECT'),
         ('smart', 'SMART'),
         ('oversea', 'Oversea')],
        string='Transfer Type',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        readonly=True,
    )
    number_cheque = fields.Char(
        string='Number Cheque',
        readonly=True,
    )
    income_tax_form = fields.Selection(
        [('pnd1', 'PND1'),
         ('pnd3', 'PND3'),
         ('pnd3a', 'PND3a'),
         ('pnd53', 'PND53')],
        string='Income Tax Form',
        readonly=True,
    )
    payment_export_id = fields.Many2one(
        'payment.export',
        string='Payment Export',
        readonly=True,
    )
    voucher_posting_date = fields.Date(
        string='Voucher Posting Date',
        readonly=True,
    )
    voucher_document_origin = fields.Char(
        string='Voucher Document Origin',
        readonly=True,
    )
    voucher_move_id = fields.Many2one(
        'account.move',
        string='Voucher Move',
        readonly=True,
    )
    payment_method_id = fields.Many2one(
        'account.journal',
        string='Payment Method',
        readonly=True,
    )
    voucher_date_value = fields.Date(
        string='Value Date',
        readonly=True,
    )
    supplier_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Supplier Bank Account',
        readonly=True,
    )
    receipt_type = fields.Selection(
        [('cash', 'Cash'),
         ('credit', 'Credit'),
         ('transfer', 'Transfer'),
         ('cheque', 'Cheque')],
        string='Receipt Type',
        readonly=True,
    )
    number_preprint = fields.Char(
        string='Preprint Number',
        readonly=True,
    )

    def _get_sql_select_dict(self):
        """
        Prefix SQL Select (Prefix + <original column>)
        1. Account Move Line (move_line_<original column>)
           Ex: move_line_name
        2. Account Move (move_<original column>)
           Ex: move_name
        3. Account Invoice (invoice_<original column>)
           Ex: invoice_name
        4. Interface Account Entry (interface_<original column>)
           Ex: interface_name
        5. Account Account (account_<original column>)
           Ex: account_name
        6. Account Voucher (voucher_<original column>)
           Ex: voucher_name

        Return
        {'account.move.line': 'aml.name AS move_line_name, ...'
         'account.move': 'am.name AS move_name, ...', ...}
        """
        model_dict = {
            'account.move.line': ('aml.', 'move_line_'),
            'account.move': ('am.', 'move_'),
            'account.invoice': ('ai.', 'invoice_'),
            'interface.account.entry': ('iae.', 'interface_'),
            'account.account': ('aa.', 'account_'),
            'account.voucher': ('av.', 'voucher_')
        }
        sql_select_dict = {}
        for model in model_dict.keys():
            # Get all columns (Convert to tuple list)
            column_tuple_list = self.pool.get(model)._columns.items()
            # Filter column only store in database
            field_types = [
                openerp.osv.fields.one2many, openerp.osv.fields.many2many,
                openerp.osv.fields.function, openerp.osv.fields.related]
            column_dict = \
                dict(filter(lambda l: type(l[1]) not in
                            (field_types[0], field_types[1],
                             field_types[2], field_types[3]) or
                            (type(l[1]) in (field_types[2], field_types[3]) and
                            l[1].store is not False), column_tuple_list))
            columns = column_dict.keys()
            prefix1, prefix2 = model_dict[model][0], model_dict[model][1]
            sql_select_dict[model] = \
                ', '.join(map(lambda x: '%s%s AS %s%s'
                              % (prefix1, x, prefix2, x), columns))
        return sql_select_dict

    def _get_sql_select(self):
        sql_select = """
            /* Invoice */
            invoice_move_table.move_line_account_id AS account_id,
            invoice_move_table.move_line_partner_id AS partner_id,
            invoice_move_table.move_id AS invoice_move_id,
            invoice_move_table.move_date_document AS invoice_document_date,
            invoice_move_table.move_date AS invoice_posting_date,
            invoice_move_table.move_name AS document_number,
            invoice_move_table.invoice_supplier_invoice_number
                AS supplier_invoice_number,
            invoice_move_table.invoice_purchase_billing_id
                AS purchase_billing_id,
            invoice_move_table.invoice_id,
            invoice_move_table.move_line_period_id AS period_id,
            invoice_move_table.move_line_date_maturity AS date_due_invoice,
            invoice_move_table.invoice_state,
            invoice_move_table.invoice_source_document_id
                AS source_document_id,
            invoice_move_table.invoice_amount_untaxed AS amount_untaxed,
            invoice_move_table.move_line_id AS invoice_move_line_id,
            invoice_move_table.invoice_amount_tax AS amount_tax,
            invoice_move_table.move_line_currency_id AS currency_id,
            invoice_move_table.move_narration AS invoice_narration,
            invoice_move_table.move_write_uid AS invoice_move_write_uid,
            invoice_move_table.interface_system_id AS system_id,
            invoice_move_table.interface_name AS document_origin,
            invoice_move_table.move_line_reconcile_id AS reconcile_id,
            CASE WHEN invoice_move_table.move_line_section_id IS NOT NULL THEN
            CONCAT('res.section,', invoice_move_table.move_line_section_id)
            WHEN invoice_move_table.move_line_project_id IS NOT NULL THEN
            CONCAT('res.project,', invoice_move_table.move_line_project_id)
            WHEN invoice_move_table.move_line_personnel_costcenter_id
            IS NOT NULL THEN CONCAT('res.personnel.costcenter,',
            invoice_move_table.move_line_personnel_costcenter_id)
            WHEN invoice_move_table.move_line_invest_asset_id IS NOT NULL THEN
            CONCAT('res.invest.asset,',
            invoice_move_table.move_line_invest_asset_id)
            WHEN invoice_move_table.move_line_invest_construction_id
            IS NOT NULL THEN CONCAT('res.invest.construction,',
            invoice_move_table.move_line_invest_construction_id)
            ELSE NULL END AS budget,
            invoice_move_table.move_line_charge_type AS charge_type,
            invoice_move_table.move_line_activity_group_id
            AS activity_group_id,
            invoice_move_table.move_line_activity_id AS activity_id,
            invoice_move_table.move_line_name,
            invoice_move_table.move_doctype AS doctype,
            invoice_move_table.move_journal_id AS journal_id,
            invoice_move_table.move_line_docline_seq AS docline_seq,
            invoice_move_table.move_line_fund_id AS fund_id,
            invoice_move_table.move_line_cost_control_type_id
            AS cost_control_type_id,
            invoice_move_table.move_line_cost_control_id AS cost_control_id,
            invoice_move_table.move_line_costcenter_id AS costcenter_id,
            invoice_move_table.move_line_project_id AS project_id,
            invoice_move_table.move_line_mission_id AS mission_id,
            invoice_move_table.invoice_cancel_move_id AS cancel_move_id,
            invoice_move_table.invoice_payment_term AS payment_term,

            /* Voucher */
            voucher_move_table.move_name AS voucher_number,
            voucher_move_table.move_line_id AS voucher_move_line_id,
            voucher_move_table.voucher_transfer_type AS transfer_type,
            voucher_move_table.voucher_id,
            voucher_move_table.voucher_number_cheque AS number_cheque,
            voucher_move_table.voucher_income_tax_form AS income_tax_form,
            voucher_move_table.voucher_payment_export_id AS payment_export_id,
            voucher_move_table.move_date AS voucher_posting_date,
            voucher_move_table.interface_name AS voucher_document_origin,
            voucher_move_table.move_id AS voucher_move_id,
            voucher_move_table.move_journal_id AS payment_method_id,
            voucher_move_table.voucher_date_value,
            voucher_move_table.voucher_supplier_bank_id AS supplier_bank_id,
            voucher_move_table.voucher_receipt_type AS receipt_type,
            CASE WHEN voucher_move_table.voucher_id IS NOT NULL THEN
            voucher_move_table.voucher_number_preprint
            WHEN voucher_move_table.interface_id IS NOT NULL THEN
            voucher_move_table.interface_preprint_number
            ELSE NULL END AS number_preprint
        """
        return sql_select

    def _get_invoice_sql_select(self, sql_select_dict):
        invoice_sql_select = """
            %s, %s, %s, %s, %s
        """ % (sql_select_dict['account.move.line'],
               sql_select_dict['account.move'],
               sql_select_dict['account.invoice'],
               sql_select_dict['interface.account.entry'],
               sql_select_dict['account.account'])
        return invoice_sql_select

    def _get_voucher_sql_select(self, sql_select_dict):
        voucher_sql_select = """
            %s, %s, %s, %s, %s
        """ % (sql_select_dict['account.move.line'],
               sql_select_dict['account.move'],
               sql_select_dict['account.voucher'],
               sql_select_dict['interface.account.entry'],
               sql_select_dict['account.account'])
        return voucher_sql_select

    def _get_invoice_move_table(self, sql_select_dict):
        """
        * Only account type in ('payable', 'receivable') *
        1. Show account.invoice
           1.1. Customer Invoice
           1.2. Customer Refund
           1.3. Supplier Invoice
           1.4. Supplier Refund
        2. In case cancel invoice not show in each lines but
           we can link to cancel move by cancel journal entry in tab other info
        3. Show adjustment
        """
        invoice_move_line = """
            SELECT %s
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN account_invoice ai ON am.id = ai.move_id
            LEFT JOIN interface_account_entry iae ON am.id = iae.move_id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            WHERE am.state = 'posted' AND aa.type IN ('payable', 'receivable')
                AND ((am.doctype IN ('out_invoice', 'out_refund',
                                    'out_invoice_debitnote', 'in_invoice',
                                    'in_refund', 'in_invoice_debitnote')
                      AND ai.id IS NOT NULL) OR am.doctype = 'adjustment'
                     OR iae.type = 'invoice')
        """ % (self._get_invoice_sql_select(sql_select_dict))
        return invoice_move_line

    def _get_voucher_move_table(self, sql_select_dict):
        """
        1. Show account.voucher
           1.1. Customer Payment
           1.2. Supplier Payment
        """
        voucher_move_line = """
            SELECT %s
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN account_voucher av ON am.id = av.move_id
            LEFT JOIN interface_account_entry iae ON am.id = iae.move_id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            WHERE am.state = 'posted' AND aa.type IN ('payable', 'receivable')
                AND ((am.doctype IN ('receipt', 'payment') AND
                      av.state = 'posted') OR iae.type = 'voucher')
        """ % (self._get_voucher_sql_select(sql_select_dict))
        return voucher_move_line

    def _get_other_invoice_move_table(self, sql_select_dict):
        """
        * Only account type not in ('payable', 'receivable') *
        1. Show account.invoice
           1.1. Customer Invoice
           1.2. Customer Refund
           1.3. Supplier Invoice
           1.4. Supplier Refund
        2. In case cancel invoice not show in each lines but
           we can link to cancel move by cancel journal entry in tab other info
        3. Show adjustment
        """
        other_invoice_move_table = """
            SELECT %s
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN account_invoice ai ON am.id = ai.move_id
            LEFT JOIN interface_account_entry iae ON am.id = iae.move_id
            LEFT JOIN account_account aa ON aml.account_id = aa.id
            WHERE am.state = 'posted'
                AND aa.type NOT IN ('payable', 'receivable')
                AND ((am.doctype IN ('out_invoice', 'out_refund',
                                    'out_invoice_debitnote', 'in_invoice',
                                    'in_refund', 'in_invoice_debitnote')
                      AND ai.id IS NOT NULL) OR am.doctype = 'adjustment'
                     OR iae.type = 'invoice')
        """ % (self._get_invoice_sql_select(sql_select_dict))
        return other_invoice_move_table

    def _get_sql_view(self):
        # Get SQL Select Dict
        sql_select_dict = self._get_sql_select_dict()

        # SQL View
        sql_view = """
            SELECT ROW_NUMBER()
                    OVER(ORDER BY invoice_move_line_id,
                                  voucher_move_line_id) AS id,*
            FROM
                ((SELECT %s
                  FROM (%s) invoice_move_table
                  LEFT JOIN (%s) voucher_move_table ON
                    invoice_move_table.move_line_reconcile_id =
                    voucher_move_table.move_line_reconcile_id
                    OR invoice_move_table.move_line_reconcile_partial_id =
                    voucher_move_table.move_line_reconcile_partial_id)
                 UNION ALL
                 (SELECT %s
                  FROM (%s) invoice_move_table
                  LEFT JOIN (%s) invoice_move_table_2 ON
                    invoice_move_table.move_id = invoice_move_table_2.move_id
                  LEFT JOIN (%s) voucher_move_table ON
                    invoice_move_table_2.move_line_reconcile_id =
                    voucher_move_table.move_line_reconcile_id
                    OR invoice_move_table_2.move_line_reconcile_partial_id =
                    voucher_move_table.move_line_reconcile_partial_id))
                AS account_data
        """ % (self._get_sql_select(),
               self._get_invoice_move_table(sql_select_dict),
               self._get_voucher_move_table(sql_select_dict),
               self._get_sql_select(),
               self._get_other_invoice_move_table(sql_select_dict),
               self._get_invoice_move_table(sql_select_dict),
               self._get_voucher_move_table(sql_select_dict))
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class PabiCommonLoanAgreementReportView(models.Model):
    _name = 'pabi.common.loan.agreement.report.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        readonly=True,
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True,
    )
    invoice_plan_id = fields.Many2one(
        'sale.invoice.plan',
        string='Invoice Plan',
        readonly=True,
    )
    payment_id = fields.Many2one(
        'account.voucher',
        string='Payment',
        readonly=True,
    )

    def _get_sql_select(self):
        sql_select = """
            ROW_NUMBER() OVER(ORDER BY lca.id, so.id, sip.id, av.id) AS id,
            lca.id AS loan_agreement_id, so.id AS order_id,
            sip.id AS invoice_plan_id, av.id AS payment_id
        """
        return sql_select

    def _get_sql_view(self):
        sql_view = """
            SELECT %s
            FROM loan_customer_agreement lca
            LEFT JOIN sale_order so ON lca.sale_id = so.id
            LEFT JOIN sale_invoice_plan sip ON so.id = sip.order_id
            LEFT JOIN account_invoice ai ON sip.ref_invoice_id = ai.id
            LEFT JOIN (SELECT av.*, avl.invoice_id
                       FROM account_voucher_line avl
                       LEFT JOIN account_voucher av ON avl.voucher_id = av.id
                       WHERE av.state != 'cancel') av ON ai.id = av.invoice_id
        """ % (self._get_sql_select())
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


# class PabiCommonSupplierPaymentReportView(models.Model):
#     _name = 'pabi.common.supplier.payment.report.view'
#     _auto = False
#
#     id = fields.Integer(
#         string='ID',
#         readonly=True,
#     )
#     voucher_id = fields.Many2one(
#         'account.voucher',
#         string='Voucher',
#         readonly=True,
#     )
#     invoice_id = fields.Many2one(
#         'account.invoice',
#         string='Invoice',
#         readonly=True,
#     )
#     voucher_line_id = fields.Many2one(
#         'account.voucher.line',
#         string='Voucher Line',
#         readonly=True,
#     )
#     expense_id = fields.Many2one(
#         'hr.expense.expense',
#         string='Expense',
#         readonly=True,
#     )
#     fiscalyear = fields.Char(
#         string='Fiscal Year',
#         readonly=True,
#     )
#     voucher_number = fields.Char(
#         string='Voucher Number',
#         readonly=True,
#     )
#     invoice_number = fields.Char(
#         string='Invoice Number',
#         readonly=True,
#     )
#     pay_to = fields.Selection(
#         [('employee', 'Employee'),
#          ('supplier', 'Supplier'),
#          ('pettycash', 'Petty Cash'),
#          ('internal', 'Internal Charge')],
#         string='Pay Type',
#         readonly=True,
#     )
#     source_document_type = fields.Selection(
#         [('purchase', 'Purchase Order'),
#          ('sale', 'Sales Order'),
#          ('expense', 'Expense'),
#          ('advance', 'Advance')],
#         string='Source Document Type',
#         readonly=True,
#     )
#     date_due = fields.Date(
#         string='Due Date',
#         readonly=True,
#     )
#
#     def _get_sql_select(self):
#         sql_select = """
#             ROW_NUMBER() OVER(ORDER BY av.id, ai.id) AS id,
#             av.id AS voucher_id, ai.id AS invoice_id,
#             av_line.id AS voucher_line_id, ex.id AS expense_id,
#             af.name AS fiscalyear, av.number AS voucher_number,
#             ai.number AS invoice_number, ex.pay_to, ai.source_document_type,
#             ai.date_due
#         """
#         return sql_select
#
#     def _get_sql_view(self):
#         sql_select = """
#             SELECT %s
#             FROM account_voucher av
#             LEFT JOIN account_voucher_line av_line
#                 ON av.id = av_line.voucher_id
#             LEFT JOIN account_move_line am_line
#                 ON av_line.move_line_id = am_line.id
#             LEFT JOIN account_invoice ai ON am_line.move_id = ai.move_id
#             LEFT JOIN account_period ap ON av.period_id = ap.id
#             LEFT JOIN account_fiscalyear af ON ap.fiscalyear_id = af.id
#             LEFT JOIN payment_export pe ON av.payment_export_id = pe.id
#             LEFT JOIN hr_expense_expense ex ON ai.expense_id = ex.id
#             WHERE av.type = 'payment' AND av.state = 'posted'
#                 AND pe.state = 'done'
#         """ % (self._get_sql_select())
#         return sql_select
#
#     def init(self, cr):
#         tools.drop_view_if_exists(cr, self._table)
#         cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
#                    % (self._table, self._get_sql_view()))
