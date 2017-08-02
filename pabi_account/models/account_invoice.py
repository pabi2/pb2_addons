# -*- coding: utf-8 -*-
import ast
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

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
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
        readonly=True,
    )
    payment_type = fields.Selection(
        [('cheque', 'Cheque'),
         ('transfer', 'Transfer'),
         ],
        string='Payment Type',
        help="Specified Payment Type, can be used to screen Payment Method",
    )
    currency_rate = fields.Float(
        string='Currency Rate',
        compute='_compute_currency_rate',
        store=True,
    )
    ref_docs = fields.Char(
        string='Reference Doc',
        compute='_compute_ref_docs',
        store=True,
    )
    invoice_description = fields.Text(
        string='Invoice Description',
        compute='_compute_invoice_description',
        store=True,
        help="Compute summary description of entire invoice lines",
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        help="If invoice has withholding tax, this field is required.",
    )
    has_wht = fields.Boolean(
        string='Has WHT in invoice line',
        compute='_compute_has_wht',
    )
    number_preprint = fields.Char(
        string='Preprint Number',
    )
    _sql_constraints = [('number_preprint_uniq', 'unique(number_preprint)',
                        'Preparint Number must be unique!')]

    @api.multi
    @api.depends('invoice_line.invoice_line_tax_id')
    def _compute_has_wht(self):
        for rec in self:
            rec.has_wht = False
            for line in rec.invoice_line:
                for tax in line.invoice_line_tax_id:
                    if tax.is_wht:
                        rec.has_wht = True

    @api.onchange('has_wht')
    def _onchange_has_wht(self):
        self.income_tax_form = \
            self.has_wht and self.partner_id.income_tax_form or False

    @api.model
    def create(self, vals):
        """ As invoice created, set default income_tax_form, if needed """
        rec = super(AccountInvoice, self).create(vals)
        if rec.has_wht:
            rec.income_tax_form = rec.partner_id.income_tax_form
        return rec

    @api.multi
    @api.depends('invoice_line')
    def _compute_invoice_description(self):
        for invoice in self:
            description = ''
            for line in invoice.invoice_line:
                description += line.name + ' ' + \
                    '{:,}'.format(line.quantity) + \
                    (line.uos_id and (' ' + line.uos_id.name) or '') + '\n'
            invoice.invoice_description = \
                len(description) > 0 and description or False

    @api.multi
    @api.depends('tax_line',
                 'tax_line.detail_ids',
                 'tax_line.detail_ids.invoice_number')
    def _compute_ref_docs(self):
        for rec in self:
            header_text = ''
            for tax in rec.tax_line:
                for detail in tax.detail_ids:
                    if not header_text:
                        header_text = detail.invoice_number
                    else:
                        header_text = (header_text + ',' +
                                       detail.invoice_number)
                    rec.ref_docs = header_text

    @api.multi
    @api.depends('currency_id')
    def _compute_currency_rate(self):
        for rec in self:
            company = rec.company_id
            context = self._context.copy()
            ctx_date = rec.date_invoice
            if not ctx_date:
                ctx_date = fields.Date.today()
            context.update({'date': ctx_date})
            # get rate of company currency to current invoice currency
            rate = self.env['res.currency'].\
                with_context(context)._get_conversion_rate(company.currency_id,
                                                           rec.currency_id)
            rec.currency_rate = rate

    @api.multi
    @api.depends()
    def _compute_payment_count(self):
        for rec in self:
            move_ids = [move_line.move_id.id for move_line in rec.payment_ids]
            voucher_ids = self.env['account.voucher'].\
                search([('move_id', 'in', move_ids)])._ids
            rec.payment_count = len(voucher_ids)

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            invoice.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.today()})
            # Not allow negative amount
            if invoice.amount_total < 0.0:
                raise ValidationError(_('Negative total amount not allowed!'))
        return result

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        res.update({
            'taxbranch_id': line.get('taxbranch_id', False),
        })
        return res

    # We can't really use constraint, need to check on validate
    # When an invoice is saved, finally it is not negative, but beginning it
    # could be
    # --
    # @api.multi
    # @api.constrains('amount_total')
    # def _check_amount_total(self):
    #     for rec in self:
    #         print rec.amount_total
    #         if rec.amount_total < 0.0:
    #             raise Warning(_('Negative Total Amount is not allowed!'))

    @api.multi
    def action_open_payments(self):
        self.ensure_one()
        move_ids = self.payment_ids.mapped('move_id')._ids
        Voucher = self.env['account.voucher']
        voucher_ids = Voucher.search([('move_id', 'in', move_ids)])._ids
        action_id = self.env.ref('account_voucher.action_vendor_payment')
        if not action_id:
            raise ValidationError(_('No Action'))
        action = action_id.read([])[0]
        action['domain'] =\
            "[('id','in', [" + ','.join(map(str, voucher_ids)) + "])]"
        ctx = ast.literal_eval(action['context'])
        ctx.update({
            'filter_by_invoice_ids': self.ids  # account_move_line.search()
        })
        action['context'] = ctx
        return action

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice,
                           self).finalize_invoice_move_lines(move_lines)
        new_move_lines = []
        # Tax Accounts
        vats = self.env['account.tax'].search([('is_wht', '=', False)])
        tax_account_ids = vats.mapped('account_collected_id').ids
        tax_account_ids += vats.mapped('account_paid_id').ids
        for line_tuple in move_lines:
            if line_tuple[2]['account_id'] in tax_account_ids:
                line_tuple[2]['taxinvoice_taxbranch_id'] = \
                    self.taxbranch_id.id
            new_move_lines.append(line_tuple)
        return new_move_lines


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_id_readonly = fields.Many2one(
        'account.account',
        string='Account',
        related='account_id',
        readonly=True,
    )

    @api.multi
    def onchange_account_id(self, product_id, partner_id, inv_type,
                            fposition_id, account_id):
        res = super(AccountInvoiceLine, self).onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id)
        account = self.env['account.account'].browse(account_id)
        if not res.get('value'):
            res['value'] = {}
        res['value'].update({'name': account.name})
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        related='invoice_id.taxbranch_id',
        string='Tax Branch',
        readonly=True,
        store=True,
    )

    @api.model
    def _prepare_invoice_tax_detail(self):
        res = super(AccountInvoiceTax, self).\
            _prepare_invoice_tax_detail()
        res.update({'taxbranch_id': self.invoice_id.taxbranch_id.id})
        return res

    @api.model
    def move_line_get(self, invoice_id):
        res = super(AccountInvoiceTax, self).move_line_get(invoice_id)
        tax_move_by_taxbranch = self.env.user.company_id.tax_move_by_taxbranch
        if tax_move_by_taxbranch:
            invoice = self.env['account.invoice'].browse(invoice_id)
            for r in res:
                r.update({'taxbranch_id': invoice.taxbranch_id.id})
        return res
