# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.tools.float_utils import float_compare
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    journal_balance = fields.Float(
        string='Bank Account Balance',
        compute='_compute_journal_balance',
        help="Balance on selected payment's GL",
    )
    exceed_balance = fields.Boolean(
        string='Balance Exceed',
        compute='_compute_journal_balance',
        help="If amount > account balance",
    )
    use_project_journal = fields.Boolean(
        string='Use Project Bank Account',
        compute='_compute_project_journal_ids',
        help="Projects has specific payment method",
    )
    project_journal_ids = fields.Many2many(
        'account.journal',
        string='Valid Bank Account',
        compute='_compute_project_journal_ids',
        help="List of valid (intersected) Journal Bank for these projects",
    )
    force_pay = fields.Boolean(
        string='Force Payment',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=False,
        track_visibility='onchange',
        help="Force payment regardless of account balance."
    )
    bank_mandate_emp_ids = fields.Many2many(
        'hr.employee',
        'account_voucher_employee_rel',
        'voucher_id', 'employee_id',
        string='Project bank mandate(s)',
        compute='_compute_bank_mandate_emp_ids',
        store=True,
        readonly=True,
        help="Information about bank madate for this account, if any."
    )

    @api.multi
    @api.depends('journal_id')
    def _compute_bank_mandate_emp_ids(self):
        for rec in self:
            rec.bank_mandate_emp_ids = rec.journal_id.bank_mandate_emp_ids
        return True

    @api.multi
    def _compute_journal_balance(self):
        for rec in self:
            # To payment doc balance
            company_balance = rec.journal_id.default_credit_account_id.balance
            from_curreny = self.env.user.company_id.currency_id
            to_currency = rec.currency_id
            balance = from_curreny.compute(company_balance, to_currency)
            rec.journal_balance = balance
            rec.exceed_balance = float_compare(rec.amount,
                                               rec.journal_balance, 2) > 0

    @api.multi
    @api.constrains('journal_id', 'line_ids')
    def _check_project_journal(self):
        for rec in self:
            if not rec.use_project_journal:
                continue
            names = rec.project_journal_ids.mapped('name')
            name_str = ', '.join(names)
            # No mixing project and non project invoices
            invoices = rec.line_ids.mapped('invoice_id')
            invoice_lines = invoices.mapped('invoice_line')
            lines = invoice_lines.filtered(lambda l: not l.project_id)
            if lines:
                raise ValidationError(
                    _('All invoices should belong to projcts that tie to '
                      'payment method : %s') % name_str)
            # Invalid payment method only supplier payment
            if rec.type != 'receipt':
                if rec.journal_id not in rec.project_journal_ids:
                    raise ValidationError(
                        _('The selected payment method is not valid!\n'
                          'Please choose from : %s') % name_str)

    @api.model
    def _get_project_journals(self, invoices):
        """
        Find intersected journal for project specific journals
        If there are project specific journal, do not mix it with other budget
        For example,
            - Project-A : [Bank1, Bank2], Project-B : [Bank2, Bank3]
                - project_journal_ids = [Bank2]
            - Project-A : [Bank1, Bank2], Project-B : [Bank3, Bank4]
                - project_journal_ids = []
        """
        use_project_journal = False
        project_journal_ids = []
        invoice_lines = invoices.mapped('invoice_line')
        project_lines = invoice_lines.filtered('project_id')
        if project_lines:
            projects = project_lines.mapped('project_id')
            journals = projects.mapped('journal_ids')
            # If any project use specific journal
            use_project_journal = len(journals) > 0 and True or False
            # Find intersected journal_ids
            lists = [x.journal_ids.ids for x in projects]
            project_journal_ids = list(set(lists[0]).intersection(*lists))
        return (use_project_journal, project_journal_ids)

    @api.model
    def default_get(self, fields):
        res = super(AccountVoucher, self).default_get(fields)
        invoice_ids = self._context.get('filter_invoices', False)
        if invoice_ids:
            invoices = self.env['account.invoice'].browse(invoice_ids)
            use_project_journal, project_journal_ids = \
                self._get_project_journals(invoices)
            res['use_project_journal'] = use_project_journal
            res['project_journal_ids'] = project_journal_ids
            if project_journal_ids and len(project_journal_ids) == 1:
                res['journal_id'] = project_journal_ids[0]
        return res

    @api.multi
    def _compute_project_journal_ids(self):
        for rec in self:
            invoices = rec.line_ids.mapped('invoice_id')
            use_project_journal, project_journal_ids = \
                self._get_project_journals(invoices)
            rec.use_project_journal = use_project_journal
            rec.project_journal_ids = project_journal_ids

    @api.multi
    def proforma_voucher(self):
        for rec in self:
            if rec.type != 'payment':
                continue
            if rec.force_pay:
                continue
            # A payment, and not force pay, check for balance and throw error
            if float_compare(rec.amount, rec.journal_balance, 2) == 1:
                raise ValidationError(
                    _('Pay amount (%s) exceed balance (%s)!\n') %
                    ('{:,.2f}'.format(rec.amount),
                     '{:,.2f}'.format(rec.journal_balance)))
        res = super(AccountVoucher, self).proforma_voucher()
        return res
