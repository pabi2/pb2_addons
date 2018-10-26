# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# from openerp.addons.pabi_account_move_document_ref.models.account_move \
#     import INVOICE_DOCTYPE

DOCTYPE_REPORT_MAP = {
    'receipt_customer': {
        'en': {
            'sale': False,
            'purchase': False,
            'receipt': 'receipt_customer_form_en',
            'payment': False,
        },
        'th': {
            'sale': False,
            'purchase': False,
            'receipt': 'receipt_customer_form_th',
            'payment': False,
        }
    },
    'receipt_supplier': {
        'en': {
            'sale': False,
            'purchase': False,
            'receipt': False,
            'payment': 'receipt_supplier_form_en',
        },
        'th': {
            'sale': False,
            'purchase': False,
            'receipt': False,
            'payment': 'receipt_supplier_form_th',
        }
    },
    'customer_receipt': {
        'en': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.receipt.form.en',
            'payment': False,
        },
        'th': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.receipt.form.th',
            'payment': False,
        }
    },
    'customer_receipt_voucher': {
        'en': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.receipt.voucher.form.en',
            'payment': False,
        },
        'th': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.receipt.voucher.form.th',
            'payment': False,
        }
    },
    'customer_tax_receipt': {
        'en': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.tax.receipt.form.en',
            'payment': False,
        },
        'th': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.tax.receipt.form.th',
            'payment': False,
        }
    },
    'customer_tax_receipt200': {
        'en': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.tax.receipt.200.form.en',
            'payment': False,
        },
        'th': {
            'sale': False,
            'purchase': False,
            'receipt': 'customer.tax.receipt.200.form.th',
            'payment': False,
        }
    },
}


class PrintAccountVoucherWizard(models.TransientModel):
    _name = 'print.account.voucher.wizard'

    doctype = fields.Selection(
        [('sale', 'Sale'),
         ('purchase', 'Purchase'),
         ('payment', 'Payment'),
         ('receipt', 'Receipt'), ],
        string="Doctype",
        readonly=True,
        default=lambda self: self._get_default_doctype(),
    )
    doc_print = fields.Selection(
        selection='_get_voucher_doctype',
        string="Report Type",
        required=True,
    )
    lang = fields.Selection(
        [('en', 'English'),
         ('th', 'Thai'), ],
        default='th',
        string="Language",
        required=True,
    )

    @api.model
    def _get_default_doctype(self):
        active_ids = self._context.get('active_ids')
        account_vouchers = self.env['account.voucher'].browse(active_ids)
        doctypes = list(set(account_vouchers.mapped('type')))
        if len(doctypes) > 1:
            raise ValidationError(
                _('Not allow selecting document with > 1 Doctypes'))
        # if doctypes[0] == 'payment':
        #     raise ValidationError(
        #         _('Print receipt is not available for supplier payment'))
        return doctypes[0]

    @api.multi
    def action_print_account_voucher(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        try:
            report_name = DOCTYPE_REPORT_MAP.get(self.doc_print, False).\
                get(self.lang, False).get(self.doctype, False)
        except Exception:
            raise ValidationError(_('No form for for this Doctype'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res

    @api.model
    def _get_voucher_doctype(self):
        ids = self._context.get('active_ids')
        if ids:
            voucher = self.env['account.voucher'].browse(ids[0])
            if voucher.type == 'receipt':
                return[('customer_receipt', 'Receipt'),
                       ('customer_receipt_voucher', 'Receipt Voucher'),
                       ('customer_tax_receipt', 'Tax Receipt'),
                       ('customer_tax_receipt200', 'Tax Receipt 200%'),
                       ('receipt_customer', 'Receipt For Customer'), ]
            elif voucher.type == 'payment':
                return [('receipt_supplier', 'Receipt For Supplier')]
        return []
