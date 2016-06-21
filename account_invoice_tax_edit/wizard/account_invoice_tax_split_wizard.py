# -*- coding: utf-8 -*-
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp
import itertools


class AccountInvoiceTaxSplitWizard(models.TransientModel):
    _name = "account.invoice.tax.split.wizard"

    tax_line_ids = fields.One2many(
        'account.invoice.tax.split.line',
        'wizard_id',
        string='Tax Lines',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceTaxSplitWizard, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        invoice = self.env[active_model].browse(active_id)
        res['tax_line_ids'] = []
        for line in invoice.tax_line:
            vals = {
                'tax_line_id': line.id,
                'number_split': 1,
            }
            res['tax_line_ids'].append((0, 0, vals))
        return res

    @api.multi
    def split_account_invoice_tax(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id', False)
        active_model = self._context.get('active_model')
        invoice = self.env[active_model].browse(active_id)
        invoice.manual_tax = True
        for line in self.tax_line_ids:
            # If number_split > 1
            if line.number_split > 1:
                line.tax_line_id.manual = True
                for _ in itertools.repeat(None, line.number_split-1):
                    line.tax_line_id.copy()
        return True


class AccountInvoiceTaxSplitLine(models.TransientModel):
    _name = "account.invoice.tax.split.line"

    wizard_id = fields.Many2one(
        'account.invoice.tax.split.wizard',
        string='Wizard',
        ondelete='cascade',
        index=True,
        required=True,
    )
    tax_line_id = fields.Many2one(
        'account.invoice.tax',
        string='Tax Line',
        readonly=True,
    )
    number_split = fields.Integer(
        string='Number Split',
    )
