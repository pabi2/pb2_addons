# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# from openerp.addons.pabi_account_move_document_ref.models.account_move \
#     import INVOICE_DOCTYPE

DOCTYPE_REPORT_MAP = {'invoice/refund': {
    'en': {
        'out_invoice': 'customer.invoice.en.form',
        'out_refund': 'customer.invoice.en.form',
        'out_invoice_debitnote': False,
        'in_invoice': False,
        'in_refund': False,
        'in_invoice_debitnote': False,
    },
    'th': {
        'out_invoice': 'customer.invoice.th.form',
        'out_refund': 'customer.invoice.th.form',
        'out_invoice_debitnote': False,
        'in_invoice': False,
        'in_refund': False,
        'in_invoice_debitnote': False,
    }
},
    'tax_invoice_picking': {
    'en': {
        'out_invoice': 'customer.tax.receipt.picking.form.en',
        'out_refund': 'customer.tax.receipt.picking.form.en',
        'out_invoice_debitnote': False,
        'in_invoice': False,
        'in_refund': False,
        'in_invoice_debitnote': False,
    },
    'th': {
        'out_invoice': 'customer.tax.receipt.picking.form.th',
        'out_refund': 'customer.tax.receipt.picking.form.th',
        'out_invoice_debitnote': False,
        'in_invoice': False,
        'in_refund': False,
        'in_invoice_debitnote': False,
    }
},
}


class PrintAccountInvoiceWizard(models.TransientModel):
    _name = 'print.account.invoice.wizard'

    doctype = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
    ],
        string="Doctype",
        readonly=True,
        default=lambda self: self._get_default_doctype(),
    )

    doc_print = fields.Selection([
        ('invoice/refund', 'Invoice/Refund'),
        ('tax_invoice_picking', 'Tax Invoice Picking'),
    ],
        default='invoice/refund',
        string="Report Type",
        required=True,
    )

    lang = fields.Selection([
        ('en', 'English'),
        ('th', 'Thai'),
    ],
        default='th',
        string="Language",
        required=True,
    )

    @api.model
    def _get_default_doctype(self):
        active_ids = self._context.get('active_ids')
        account_invoices = self.env['account.invoice'].browse(active_ids)
        doctypes = list(set(account_invoices.mapped('type')))
        if len(doctypes) > 1:
            raise ValidationError(
                _('Not allow selecting document with > 1 Doctypes'))
        return doctypes[0]

    @api.multi
    def action_print_account_invoice(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        try:
            report_name = DOCTYPE_REPORT_MAP.get(self.doc_print, False).\
                get(self.lang, False).get(self.doctype, False)
        except Exception:
            report_name = False
        if not report_name:
            raise ValidationError(_('No form for for this Doctype'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
