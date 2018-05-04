# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountWhtCert(models.Model):
    _inherit = 'account.wht.cert'

    @api.model
    def _prepare_wht_line(self, voucher):
        wht_lines = []
        if self._context.get('pit_withhold', False):
            for line in voucher.pit_line:
                vals = {
                    'pit_id': line.id,
                    'wht_cert_income_type': line.wht_cert_income_type,
                    'wht_cert_income_desc': line.wht_cert_income_desc,
                    'base': line.amount_income,
                    'amount': line.amount_wht,
                }
                wht_lines.append((0, 0, vals))
        else:
            wht_lines = super(AccountWhtCert,
                              self)._prepare_wht_line(voucher)
        return wht_lines

    @api.multi
    def _save_selection(self):
        self.ensure_one()
        if self._context.get('pit_withhold', False):
            if self.voucher_id:
                if not self.voucher_id.income_tax_form:
                    self.voucher_id.income_tax_form = self.income_tax_form
                self.voucher_id.tax_payer = self.tax_payer
            for line in self.wht_line:
                if line.pit_id:
                    line.pit_id.write({
                        'wht_cert_income_type': line.wht_cert_income_type,
                        'wht_cert_income_desc': line.wht_cert_income_desc,
                    })
        else:
            super(AccountWhtCert, self)._save_selection()


class WhtCertTaxLine(models.Model):
    _inherit = 'wht.cert.tax.line'

    pit_id = fields.Many2one(
        'personal.income.tax',
        string='PIT Line',
        readonly=True,
    )
