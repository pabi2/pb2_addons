# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_account_move_document_ref.models.account_move \
    import DOCTYPE_SELECT

DOCTYPE_REPORT_MAP = {
    'jasper': {
        'incoming_shipment': False,
        'delivery_order': False,
        'internal_transfer': False,
        'bank_receipt': 'bank.receipt.voucher',
        'out_invoice': 'invoice.voucher',
        'out_refund': 'invoice.voucher',
        'out_invoice_debitnote': False,
        'in_invoice': 'invoice.voucher',
        'in_refund': 'invoice.voucher',
        'in_invoice_debitnote': False,
        'receipt': 'receipt.voucher',
        'payment': 'payment.voucher',
        'employee_expense': False,
        'interface_account': False,
        'purchase_request': False,
        'purchase_order': False,
        'sale_order': False,
        'adjustment': 'adjustment.voucher'
    },
    'qweb': {
        'incoming_shipment': False,
        'delivery_order': 'pabi_forms.report_delivery_order_voucher',
        'internal_transfer': False,
        'bank_receipt': 'pabi_forms.report_bank_receipt_voucher',
        'out_invoice': 'pabi_forms.report_invoice_voucher',
        'out_refund': 'pabi_forms.report_invoice_voucher',
        'out_invoice_debitnote': False,
        'in_invoice': 'pabi_forms.report_invoice_voucher',
        'in_refund': 'pabi_forms.report_invoice_voucher',
        'in_invoice_debitnote': False,
        'receipt': 'pabi_forms.report_receipt_voucher',
        'payment': 'pabi_forms.report_payment_voucher',
        'employee_expense': 'pabi_forms.report_employee_expense_voucher',
        'interface_account': 'pabi_forms.report_interface_account_voucher',
        'purchase_request': False,
        'purchase_order': False,
        'sale_order': False,
        'adjustment': 'pabi_forms.report_adjustment_voucher',
        'salary_expense': 'pabi_forms.report_salary_expense_voucher',
    }
}


class PrintVoucherWizard(models.TransientModel):
    _name = 'print.voucher.wizard'

    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string="Doctype",
        readonly=True,
        default=lambda self: self._get_default_doctype(),
    )
    report_type = fields.Selection(
        [('qweb', 'QWeb'), ('jasper', 'Jasper')],
        string="Type",
        required=True,
        default='qweb',
    )

    @api.model
    def _get_default_doctype(self):
        active_ids = self._context.get('active_ids')
        account_moves = self.env['account.move'].browse(active_ids)
        doctypes = list(set(account_moves.mapped('doctype')))
        if len(doctypes) > 1:
            raise ValidationError(
                _('Not allow selecting document with > 1 Doctypes'))
        return doctypes[0]

    @api.multi
    def action_print_voucher(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        report_name = DOCTYPE_REPORT_MAP.get(self.report_type, {}) \
            .get(self.doctype, False)
        if not report_name:
            raise ValidationError(_('No form for for this Doctype'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
