# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.l10n_th_account.models.account_voucher \
    import WHT_CERT_INCOME_TYPE, TAX_PAYER
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class PrintWhtCertWizard(models.Model):
    _name = 'print.wht.cert.wizard'
    _rec_name = 'voucher_id'

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
    )
    company_partner_id = fields.Many2one(
        'res.partner',
        string='Company',
        readonly=True,
    )
    supplier_partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
    )
    company_taxid = fields.Char(
        related='company_partner_id.vat',
        string='Company Tax ID',
        readonly=True,
    )
    supplier_taxid = fields.Char(
        related='supplier_partner_id.vat',
        string='Supplier Tax ID',
        readonly=True,
    )
    supplier_address = fields.Char(
        string='Supplier Address',
        compute='_compute_address',
        readonly=True,
    )
    company_address = fields.Char(
        string='Company Address',
        compute='_compute_address',
        readonly=True,
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        required=True,
    )
    wht_sequence_display = fields.Char(
        string='WHT Sequence',
        related='voucher_id.wht_sequence_display',
    )
    wht_line = fields.One2many(
        'wht.cert.tax.line',
        'wizard_id',
        string='Withholding Line',
    )
    tax_payer = fields.Selection(
        TAX_PAYER,
        string='Tax Payer',
        default='withholding',
        required=True,
    )
    # Computed fields to be displayed in WHT Cert.
    x_voucher_number = fields.Char(compute='_compute_cert_fields')
    x_date_value = fields.Date(compute='_compute_cert_fields')
    x_company_name = fields.Char(compute='_compute_cert_fields')
    x_supplier_name = fields.Char(compute='_compute_cert_fields')
    x_company_taxid = fields.Char(compute='_compute_cert_fields')
    x_supplier_taxid = fields.Char(compute='_compute_cert_fields')
    x_supplier_address = fields.Char(compute='_compute_cert_fields')
    x_company_address = fields.Char(compute='_compute_cert_fields')
    x_pnd1 = fields.Char(compute='_compute_cert_fields')
    x_pnd3 = fields.Char(compute='_compute_cert_fields')
    x_pnd53 = fields.Char(compute='_compute_cert_fields')
    x_wht_sequence_display = fields.Char(compute='_compute_cert_fields')
    x_withholding = fields.Char(compute='_compute_cert_fields')
    x_paid_one_time = fields.Char(compute='_compute_cert_fields')
    x_total_base = fields.Float(compute='_compute_cert_fields')
    x_total_tax = fields.Float(compute='_compute_cert_fields')
    x_type_1_base = fields.Float(compute='_compute_cert_fields')
    x_type_1_tax = fields.Float(compute='_compute_cert_fields')
    x_type_2_base = fields.Float(compute='_compute_cert_fields')
    x_type_2_tax = fields.Float(compute='_compute_cert_fields')
    x_type_3_base = fields.Float(compute='_compute_cert_fields')
    x_type_3_tax = fields.Float(compute='_compute_cert_fields')
    x_type_5_base = fields.Float(compute='_compute_cert_fields')
    x_type_5_tax = fields.Float(compute='_compute_cert_fields')
    x_type_5_desc = fields.Float(compute='_compute_cert_fields')
    x_type_6_base = fields.Float(compute='_compute_cert_fields')
    x_type_6_tax = fields.Float(compute='_compute_cert_fields')
    x_type_6_desc = fields.Float(compute='_compute_cert_fields')
    x_signature = fields.Char(compute='_compute_cert_fields')

    @api.multi
    def _compute_cert_fields(self):
        for rec in self:
            voucher = rec.voucher_id
            company = self.env.user.company_id.partner_id
            supplier = voucher.partner_id
            rec.x_voucher_number = voucher.number
            rec.x_date_value = voucher.date_value
            rec.x_company_name = company.display_name
            rec.x_supplier_name = supplier.display_name
            rec.x_company_taxid = len(company.vat) == 13 and company.vat or ''
            rec.x_supplier_taxid = \
                len(supplier.vat) == 13 and supplier.vat or ''
            rec.x_supplier_address = rec.supplier_address
            rec.x_company_address = rec.company_address
            rec.x_pnd1 = voucher.income_tax_form == 'pnd1' and 'X' or ''
            rec.x_pnd3 = voucher.income_tax_form == 'pnd3' and 'X' or ''
            rec.x_pnd53 = voucher.income_tax_form == 'pnd53' and 'X' or ''
            rec.x_wht_sequence_display = voucher.wht_sequence_display
            rec.x_withholding = \
                voucher.tax_payer == 'withholding' and 'X' or ''
            rec.x_paid_one_time = \
                voucher.tax_payer == 'paid_one_time' and 'X' or ''
            rec.x_total_base = rec._get_summary_by_type('base')
            rec.x_total_tax = rec._get_summary_by_type('tax')
            rec.x_type_1_base = rec._get_summary_by_type('base', '1')
            rec.x_type_1_tax = rec._get_summary_by_type('tax', '1')
            rec.x_type_2_base = rec._get_summary_by_type('base', '2')
            rec.x_type_2_tax = rec._get_summary_by_type('tax', '2')
            rec.x_type_3_base = rec._get_summary_by_type('base', '3')
            rec.x_type_3_tax = rec._get_summary_by_type('tax', '3')
            rec.x_type_5_base = rec._get_summary_by_type('base', '5')
            rec.x_type_5_tax = rec._get_summary_by_type('tax', '5')
            rec.x_type_5_desc = rec._get_summary_by_type('desc', '5')
            rec.x_type_6_base = rec._get_summary_by_type('base', '6')
            rec.x_type_6_tax = rec._get_summary_by_type('tax', '6')
            rec.x_type_6_desc = rec._get_summary_by_type('desc', '6')
            rec.x_signature = voucher.validate_user_id.display_name

    @api.multi
    def _compute_address(self):
        for rec in self:
            rec.company_address = \
                self._prepare_address(rec.company_partner_id)
            rec.supplier_address = \
                self._prepare_address(rec.supplier_partner_id)

    @api.model
    def _prepare_wht_line(self, voucher):
        wht_lines = []
        for line in voucher.tax_line_wht:
            vals = {
                'voucher_tax_id': line.id,
                'invoice_id': line.invoice_id.id,
                'wht_cert_income_type': line.wht_cert_income_type,
                'wht_cert_income_desc': line.wht_cert_income_desc,
                'base': -line.base,
                'amount': -line.amount,
            }
            wht_lines.append((0, 0, vals))
        return wht_lines

    @api.model
    def default_get(self, fields):
        res = super(PrintWhtCertWizard, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        voucher = self.env[active_model].browse(active_id)
        company_partner = self.env.user.company_id.partner_id
        supplier = voucher.partner_id
        res['voucher_id'] = voucher.id
        res['company_partner_id'] = company_partner.id
        res['supplier_partner_id'] = supplier.id
        res['income_tax_form'] = (voucher.income_tax_form or
                                  supplier.income_tax_form)
        res['tax_payer'] = (voucher.tax_payer or False)
        res['wht_line'] = self._prepare_wht_line(voucher)
        return res

    @api.multi
    def run_report(self):
        self._save_selection()
        self.voucher_id._assign_wht_sequence()

    @api.multi
    def write(self, vals):
        res = super(PrintWhtCertWizard, self).write(vals)
        if 'wht_line' in vals:
            for rec in self:
                rec._save_selection()
        return res

    @api.multi
    def _get_summary_by_type(self, column, ttype='all'):
        self.ensure_one()
        wht_lines = self.wht_line
        if ttype != 'all':
            wht_lines = wht_lines.filtered(lambda l:
                                           l.wht_cert_income_type == ttype)
        if column == 'base':
            return round(sum([x.base for x in wht_lines]), 2)
        if column == 'tax':
            return round(sum([x.amount for x in wht_lines]), 2)
        if column == 'desc':
            descs = [x.wht_cert_income_desc for x in wht_lines]
            descs = filter(lambda x: x is not False and x != '', descs)
            return ', '.join(descs)

    @api.model
    def _prepare_address(self, partner):
        address_list = [partner.street, partner.street2, partner.city,
                        partner.township_id.name, partner.district_id.name,
                        partner.province_id.name, partner.zip, ]
        address_list = filter(lambda x: x is not False and x != '',
                              address_list)
        return ' '.join(address_list).strip()

    @api.multi
    def _save_selection(self):
        self.ensure_one()
        if not self.voucher_id.income_tax_form:
            self.voucher_id.income_tax_form = self.income_tax_form
        self.voucher_id.tax_payer = self.tax_payer
        for line in self.wht_line:
            line.voucher_tax_id.write({
                'wht_cert_income_type': line.wht_cert_income_type,
                'wht_cert_income_desc': line.wht_cert_income_desc,
            })
        return


class WhtCertTaxLine(models.Model):
    _name = 'wht.cert.tax.line'

    wizard_id = fields.Many2one(
        'print.wht.cert.wizard',
        string='Wizard',
        index=True,
    )
    voucher_tax_id = fields.Many2one(
        'account.voucher.tax',
        string='Voucher Tax Line',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        related='voucher_tax_id.invoice_id',
        string='Invoice',
        readonly=True,
    )
    wht_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
        required=True,
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
        size=50,
        required=False,
    )
    base = fields.Float(
        string='Base Amount',
        readonly=True,
    )
    amount = fields.Float(
        string='Tax Amount',
        readonly=True,
    )

    @api.onchange('wht_cert_income_type')
    def _onchange_wht_cert_income_type(self):
        if self.wht_cert_income_type:
            select_dict = dict(WHT_CERT_INCOME_TYPE)
            self.wht_cert_income_desc = select_dict[self.wht_cert_income_type]
        else:
            self.wht_cert_income_desc = False
