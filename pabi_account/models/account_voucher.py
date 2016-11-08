# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


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
        help="Specified Payment Type, can be used to screen Payment Method",
    )
    supplier_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Supplier Bank Account',
        domain="[('partner_id', '=', partner_id)]",
    )
    supplier_bank_branch = fields.Char(
        string='Supplier Bank Branch',
        related='supplier_bank_id.branch_cheque',
        readonly=True,
    )

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
                    if line.move_line_id.doc_ref:
                        invoices_text.append(line.move_line_id.doc_ref)
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
        # for voucher in self:
        #     taxbranchs = []
        #     for line in voucher.line_ids:
        #         if line.amount or line.amount_wht or line.amount_retention:
        #             taxbranchs.append(line.supplier_invoice_taxbranch_id.id)
        #     if len(list(set(taxbranchs))) > 1:
        #         raise UserError(_('Mixing invoices of different '
        #                           'tax branch is not allowed!'))
        result = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            voucher.write({'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.today()})
        return result

    # Voucher Selection
    # @api.model
    # def create(self, vals):
    #     print vals
    #     # DR
    #     line_dr_ids = []
    #     for line in vals.get('line_dr_ids', []):
    #         if line[2]['amount'] > 0.0:
    #             line_dr_ids.append(line)
    #     vals.update({'line_dr_ids': line_dr_ids})
    #     # CR
    #     line_cr_ids = []
    #     for line in vals.get('line_cr_ids', []):
    #         if line[2]['amount'] > 0.0:
    #             line_cr_ids.append(line)
    #     vals.update({'line_cr_ids': line_cr_ids})
    #     # --
    #     voucher = super(AccountVoucher, self).create(vals)
    #     return voucher

    # @api.multi
    # def write(self, vals):
    #     res = super(AccountVoucher, self).write(vals)
    #     # Delete all amount zero lines
    #     for voucher in self:
    #         # Voucher Line
    #         zero_lines = voucher.line_ids.filtered(lambda l: not l.amount)
    #         zero_lines.unlink()
    #         # Tax Line
    #         zero_lines = voucher.tax_line.filtered(lambda l: not l.amount)
    #         zero_lines.unlink()
    #     return res


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    # Voucher Selection
    # select = fields.Boolean(
    #     string='Select',
    #     default=False,
    # )
    #
    # @api.onchange('select')
    # def _onchange_select(self):
    #     if self.select:
    #         self.reconcile = True
    #     else:
    #         self.reconcile = False
    #         self.amount = False
    # --

    @api.model
    def get_suppl_inv_taxbranch(self, move_line_id):
        move_line = self.env['account.move.line'].\
            browse(move_line_id)
        return (move_line.invoice and
                move_line.invoice.taxbranch_id or False)

    @api.depends('move_line_id', 'voucher_id', 'amount')
    def _compute_supplier_invoice_taxbranch(self):
        for line in self:
            if line.move_line_id:
                line.supplier_invoice_taxbranch_id =\
                    self.get_suppl_inv_taxbranch(line.move_line_id.id)

    supplier_invoice_taxbranch_id = fields.Many2one(
        'res.taxbranch',
        compute='_compute_supplier_invoice_taxbranch',
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
    def _prepare_voucher_tax_detail(self, voucher_tax):
        res = super(AccountVoucherTax, self).\
            _prepare_voucher_tax_detail(voucher_tax)
        res.update({'taxbranch_id': voucher_tax.invoice_id.taxbranch_id.id})
        return res

    @api.model
    def move_line_get(self, voucher):
        """ Normal Tax: Use invoice's tax branch for tax move line
            WHT: Use a centralized tax branch """
        res = super(AccountVoucherTax, self).move_line_get(voucher)
        taxbranch_id = False
        for line in voucher.line_ids:
            if line.amount or line.amount_wht or line.amount_retention:
                taxbranch_id = line.supplier_invoice_taxbranch_id.id
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
