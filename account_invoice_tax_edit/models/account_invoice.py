# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    manual_tax = fields.Boolean(
        string='Manual Tax',
        default=False,
    )

    @api.multi
    def button_reset_original_tax(self):
        for invoice in self:
            invoice.tax_line.unlink()
            invoice.manual_tax = False
        self.button_reset_taxes()
        return True

    @api.model
    def check_missing_tax(self):
        res = super(AccountInvoice, self).check_missing_tax()
        if self.manual_tax:
            res = False
        return res


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    invoice_number = fields.Char(
        string='Supplier Invoice Number'
    )
    invoice_date = fields.Date(
        string='Supplier Invoice Date'
    )

    @api.model
    def _prepare_tax_line_from_obj(self, line):
        return {'name': line['name'],
                'account_id': line['account_id'].id,
                'base': line['base'],
                'amount': line['amount'],
                'account_analytic_id': line['account_analytic_id'].id,
                'base_code_id': line['base_code_id'].id,
                'tax_code_id': line['tax_code_id'].id,
                'base_amount': line['base_amount'],
                'tax_amount': line['tax_amount'],
                'factor_base': line['factor_base'],
                'factor_tax': line['factor_tax'], }

    @api.model
    def _prepare_tax_line_from_dict(self, line):
        return {'name': line['name'],
                'account_id': line['account_id'],
                'base': line['base'],
                'amount': line['amount'],
                'account_analytic_id': line['account_analytic_id'],
                'base_code_id': line['base_code_id'],
                'tax_code_id': line['tax_code_id'],
                'base_amount': line['base_amount'],
                'tax_amount': line['tax_amount'],
                'factor_base': line['factor_base'],
                'factor_tax': line['factor_tax'], }

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceTax, self).default_get(fields)
        tax_line = self._context.get('tax_line')
        if tax_line:
            last_tax_line = tax_line[-1]
            if last_tax_line[0] == 4:  # 4 is existing db record
                line = self.env['account.invoice.tax'].browse(last_tax_line[1])
                res.update(self._prepare_tax_line_from_obj(line))
            if last_tax_line[0] == 0:  # 4 is existing db record
                line = last_tax_line[2]
                res.update(self._prepare_tax_line_from_dict(line))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
