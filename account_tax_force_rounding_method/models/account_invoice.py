# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    force_tax_rounding_method = fields.Selection(
        [('round_per_line', 'Round per line'),
         ('round_globally', 'Round globally')],
        string='Force Tax Rounding',
    )


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    @api.v8
    def compute(self, invoice):
        methods = invoice.sale_ids.mapped('force_tax_rounding_method')
        if len(methods) > 1:
            raise ValidationError(_('> 1 force rounding method!'))
        if len(methods) == 1:
            self = self.with_context(force_tax_rounding_method=methods[0])
        return super(AccountInvoiceTax, self).compute(invoice)
