# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.addons.l10n_th_account.models.account_voucher \
    import WHT_CERT_INCOME_TYPE, TAX_PAYER
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM


class PrintWhtCertWizard(models.TransientModel):
    _name = 'print.wht.cert.wizard'

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

    @api.one
    @api.depends('company_partner_id', 'supplier_partner_id')
    def _compute_address(self):
        self.company_address = self._prepare_address(self.company_partner_id)
        self.supplier_address = self._prepare_address(self.supplier_partner_id)

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
        res['wht_sequence_display'] = voucher.wht_sequence_display
        res['tax_payer'] = (voucher.tax_payer or False)
        res['wht_line'] = []
        for line in voucher.tax_line_wht:
            vals = {
                'voucher_tax_id': line.id,
                'invoice_id': line.invoice_id.id,
                'wht_cert_income_type': line.wht_cert_income_type,
                'wht_cert_income_desc': line.wht_cert_income_desc,
                'base': -line.base,
                'amount': -line.amount,
            }
            res['wht_line'].append((0, 0, vals))
        return res

    @api.multi
    def run_report(self):
        data = {'parameters': {}}
        self._save_selection()
        self.voucher_id._assign_wht_sequence()
        form_data = self._get_form_data()
        data['parameters'] = form_data
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_withholding_cert',
            'datas': data,
            'context': {'lang': 'th_TH'},
        }
        return res

    @api.model
    def _get_form_data(self):
        """ Data to pass as parameter in iReport """
        data = {}
        TH = {'lang': 'th_TH'}
        voucher = self.with_context(TH).voucher_id
        data['voucher_number'] = voucher.number
        data['date_value'] = voucher.date_value
        company = self.with_context(TH).env.user.company_id.partner_id
        supplier = voucher.partner_id
        if not company.vat or not supplier.vat:
            raise UserError(_('No Tax ID on Company or Supplier'))
        data['company_name'] = company.name_get()[0][1]
        data['supplier_name'] = supplier.name_get()[0][1]
        company_taxid = len(company.vat) == 13 and company.vat or ''
        data['company_taxid'] = list(company_taxid)
        supplier_taxid = len(supplier.vat) == 13 and supplier.vat or ''
        data['supplier_taxid'] = list(supplier_taxid)
        data['company_address'] = self.company_address
        data['supplier_address'] = self.supplier_address
        data['pnd3'] = voucher.income_tax_form == 'pnd3' and 'X' or ''
        data['pnd53'] = voucher.income_tax_form == 'pnd53' and 'X' or ''
        data['wht_sequence_display'] = voucher.wht_sequence_display
        data['withholding'] = voucher.tax_payer == 'withholding' and 'X' or ''
        data['paid_one_time'] = (voucher.tax_payer == 'paid_one_time' and
                                 'X' or '')
        data['total_base'] = self._get_summary_by_type('base')
        data['total_tax'] = self._get_summary_by_type('tax')
        data['type_1_base'] = self._get_summary_by_type('base', '1')
        data['type_1_tax'] = self._get_summary_by_type('tax', '1')
        data['type_2_base'] = self._get_summary_by_type('base', '2')
        data['type_2_tax'] = self._get_summary_by_type('tax', '2')
        data['type_3_base'] = self._get_summary_by_type('base', '3')
        data['type_3_tax'] = self._get_summary_by_type('tax', '3')
        data['type_5_base'] = self._get_summary_by_type('base', '5')
        data['type_5_tax'] = self._get_summary_by_type('tax', '5')
        data['type_5_desc'] = self._get_summary_by_type('desc', '5')
        data['type_6_base'] = self._get_summary_by_type('base', '6')
        data['type_6_tax'] = self._get_summary_by_type('tax', '6')
        data['type_6_desc'] = self._get_summary_by_type('desc', '6')
        data['signature'] = self.with_context(TH).env.user.name_get()[0][1]
        return data

    @api.model
    def _get_summary_by_type(self, column, ttype='all'):
        wht_lines = self.wht_line
        if ttype != 'all':
            wht_lines = wht_lines.filtered(lambda l:
                                           l.wht_cert_income_type == ttype)
        if column == 'base':
            return sum([x.base for x in wht_lines])
        if column == 'tax':
            return sum([x.amount for x in wht_lines])
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

    @api.model
    def _save_selection(self):
        if not self.voucher_id.income_tax_form:
            self.voucher_id.income_tax_form = self.income_tax_form
        self.voucher_id.tax_payer = self.tax_payer
        for line in self.wht_line:
            line.voucher_tax_id.write({
                'wht_cert_income_type': line.wht_cert_income_type,
                'wht_cert_income_desc': line.wht_cert_income_desc,
            })
        return


class WhtCertTaxLine(models.TransientModel):
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
