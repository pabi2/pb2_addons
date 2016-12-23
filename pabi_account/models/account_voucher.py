# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    invoices_text = fields.Char(
        size=1000,
        compute='_compute_invoices_ref',
        string='Invoices',
        store=True,
    )
    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated By',
        readonly=True,
        copy=False,
    )
    validate_date = fields.Date(
        'Validate On',
        readonly=True,
        copy=False,
    )
    total_ar_amount = fields.Float(
        compute="_compute_total_ar_ap_amount",
        string='Total AR',
        digits_compute=dp.get_precision('Account'),
    )
    total_ap_amount = fields.Float(
        compute="_compute_total_ar_ap_amount",
        string='Total AR',
        digits_compute=dp.get_precision('Account'),
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        readonly=True, states={'draft': [('readonly', False)]},
        help="Specified Payment Type, can be used to screen Payment Method",
    )
    supplier_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Supplier Bank Account',
        domain="[('partner_id', '=', partner_id)]",
        readonly=True, states={'draft': [('readonly', False)]},
    )
    supplier_bank_branch = fields.Char(
        string='Supplier Bank Branch',
        related='supplier_bank_id.branch_cheque',
        readonly=True,
    )
    narration = fields.Text(
        readonly=False,
    )
    operating_unit_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]},
    )
    writeoff_operating_unit_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]},
    )
    currency_rate = fields.Float(
        string='Currency Rate',
        compute='_compute_currency_rate',
        store=True,
    )
    voucher_description = fields.Text(
        string='Voucher Description',
        compute='_compute_voucher_description',
        help="Compute summary description of entire voucher lines",
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        compute='_compute_income_tax_form',
        store=True,
        help="Auto compute from the selected invoice",
    )
    number_preprint = fields.Char(
        string='Preprint Number',
    )
    research_type = fields.Selection(
        [('basic', 'Basic Research'),
         ('applied', 'Applied Research'),
         ],
        string='Research Type',
    )
    contract_number = fields.Char(
        string='Contract Number',
    )
    _sql_constraints = [('number_preprint_uniq', 'unique(number_preprint)',
                        'Preparint Number must be unique!')]

    @api.multi
    @api.constrains('line_ids', 'line_cr_ids', 'line_dr_ids')
    def _check_receipt_no_mixing_taxbranch(self):
        for voucher in self:
            if voucher.type == 'receipt':
                taxbranches = voucher.line_ids.mapped('invoice_taxbranch_id')
                if len(taxbranches) > 1:
                    raise ValidationError(_('Mixing invoices for different '
                                            'tax branch is not allowed!'))

    @api.multi
    @api.depends('line_ids')
    def _compute_income_tax_form(self):
        for voucher in self:
            invoices = voucher.line_ids.mapped('move_line_id.invoice')
            forms = []
            for invoice in invoices:
                if invoice.has_wht and invoice.income_tax_form:
                    forms.append(invoice.income_tax_form)
            if forms:
                if len(forms) != 1:
                    raise ValidationError(
                        _('Selected invoices has different Income Tax Form!'))
                voucher.income_tax_form = forms[0]

    @api.multi
    @api.depends('line_ids')
    def _compute_voucher_description(self):
        for voucher in self:
            items = []
            description = ''
            for line in voucher.line_ids:
                invoice = line.move_line_id.invoice
                amount = line.amount
                invoice_number = '%10s' % invoice.number
                amount_str = '%15s' % '{:,}'.format(amount)
                items.append('%s %s' % (invoice_number, amount_str))
                if len(items) == 3:
                    description += '      '.join(items) + '\n'
                    items = []
            voucher.voucher_description = description

    @api.multi
    @api.depends('currency_id')
    def _compute_currency_rate(self):
        for rec in self:
            company = rec.company_id
            context = self._context.copy()
            ctx_date = rec.date
            if not ctx_date:
                ctx_date = fields.Date.today()
            context.update({'date': ctx_date})
            # get rate of company currency to current invoice currency
            rate = self.env['res.currency'].\
                with_context(context)._get_conversion_rate(company.currency_id,
                                                           rec.currency_id)
            rec.currency_rate = rate

    @api.multi
    @api.constrains('date_value')
    def _check_date_value_same_period(self):
        for voucher in self:
            if voucher.date_value:
                Period = self.env['account.period']
                period = Period.find(voucher.date_value)[:1]
                if voucher.period_id != period:
                    raise ValidationError(
                        _('Value Date can not be in different '
                          'period as its document!'))

    @api.model
    def _get_related_invoices(self):
        doc_types = ('in_invoice', 'in_refund',)
        if self.type == 'receipt':
            doc_types = ('out_invoice', 'out_refund',)
        AccountInvoice = self.env['account.invoice']
        partner = self.partner_id.id
        invoice_ids =\
            AccountInvoice.search([('state', '=', 'open'),
                                   ('type', 'in', doc_types),
                                   ('partner_id', 'child_of', partner)]).ids
        return invoice_ids

    @api.depends()
    def _compute_total_ar_ap_amount(self):
        for record in self:
            invoice_ids = record._get_related_invoices()
            amount = 0.0
            if invoice_ids:
                invoices = self.env['account.invoice'].browse(invoice_ids)
                amount = sum([i.amount_total for i in invoices])
            if record.type == 'receipt':
                record.total_ar_amount = amount
            elif record.type == 'payment':
                record.total_ap_amount = amount

    @api.depends('line_ids')
    def _compute_invoices_ref(self):
        for voucher in self:
            invoices_text = []
            limit = 3
            i = 0
            for line in voucher.line_ids:
                if line.move_line_id and i < limit:
                    if line.move_line_id.document:
                        invoices_text.append(line.move_line_id.document)
                    i += 1
            voucher.invoices_text = ", ".join(invoices_text)
            if len(voucher.line_ids) > limit:
                voucher.invoices_text += ', ...'

    @api.multi
    def action_open_invoices(self):
        self.ensure_one()
        invoice_ids = self._get_related_invoices()
        action_id = False
        if self.type == 'receipt':
            action_id = self.env.ref('account.action_invoice_tree1')
        else:
            action_id = self.env.ref('account.action_invoice_tree2')
        if action_id:
            action = action_id.read([])[0]
            action['domain'] =\
                "[('id','in', ["+','.join(map(str, invoice_ids))+"])]"
            return action
        return True

    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            voucher.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.today()})
        return result


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    invoice_description = fields.Text(
        related='invoice_id.invoice_description',
        string='Invoice Description',
        readonly=True,
    )
    invoice_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        related='move_line_id.invoice.taxbranch_id',
        string='Taxbranch',
        store=True,
    )


class AccountVoucherTax(models.Model):
    _inherit = "account.voucher.tax"

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        related='invoice_id.taxbranch_id',
        string='Tax Branch',
        readonly=True,
        store=True,
    )

    @api.model
    def _prepare_voucher_tax_detail(self):
        res = super(AccountVoucherTax, self)._prepare_voucher_tax_detail()
        res.update({'taxbranch_id': self.invoice_id.taxbranch_id.id})
        return res

    @api.model
    def move_line_get(self, voucher):
        """ Normal Tax: Use invoice's tax branch for tax move line
            WHT: Use a centralized tax branch """
        res = super(AccountVoucherTax, self).move_line_get(voucher)
        taxbranch_id = False
        for line in voucher.line_ids:
            if line.amount or line.amount_wht or line.amount_retention:
                taxbranch_id = line.invoice_taxbranch_id.id
        tax_move_by_taxbranch = self.env.user.company_id.tax_move_by_taxbranch
        if tax_move_by_taxbranch:
            wht_taxbranch_id = self.env.user.company_id.wht_taxbranch_id.id
            for r in res:
                if 'tax_code_type' in r and r['tax_code_type'] == 'wht' \
                        and wht_taxbranch_id:
                    r.update({'taxbranch_id': wht_taxbranch_id})
                else:
                    r.update({'taxbranch_id': taxbranch_id})
        return res
