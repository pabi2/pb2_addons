# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    tax_mismatch = fields.Boolean(
        string='Tax Mismatch',
        compute='_compute_tax_mismatch',
        help="True if untaxed + tax != total",
    )

    @api.multi
    def _compute_tax_mismatch(self):
        for rec in self:
            amount = rec.amount_untaxed + rec.amount_tax
            if float_compare(amount, rec.amount_total, 2) == 0:
                rec.tax_mismatch = False
            else:
                rec.tax_mismatch = True
        return True

    @api.multi
    def fix_tax_rounding(self):
        """ This method will,
            1) Change tax counding method
            2) Calc Tax
            3) Set rounding method back
        """
        company = self.env.user.company_id
        old_method = company.tax_calculation_rounding_method
        new_method = (old_method == 'round_per_line') and \
            'round_globally' or 'round_per_line'
        vals = {'tax_calculation_rounding_method': new_method}
        company.write(vals)
        for invoice in self:
            invoice.invoice_line._compute_price()
            invoice._compute_amount()
        vals = {'tax_calculation_rounding_method': old_method}
        company.write(vals)
        return True
