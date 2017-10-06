# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_account_move_document_ref.models.account_move \
    import DOCTYPE_SELECT

DOCTYPE_REPORT_MAP = {'incoming_shipment': False,
                      'delivery_order': False,
                      'internal_transfer': False,
                      'bank_receipt': 'bank.receipt.voucher',
                      'out_invoice': 'invoice.voucher',
                      'out_refund': 'invoice.voucher',
                      'out_invoice_debitnote': False,
                      'in_invoice': 'invoice.voucher',
                      'in_refund': 'invoice.voucher',
                      'in_invoice_debitnote': False,
                      'receipt': 'payment.voucher',
                      'payment': 'payment.voucher',
                      'employee_expense': False,
                      'interface_account': False,
                      'purchase_request': False,
                      'purchase_order': False,
                      'sale_order': False,
                      'adjustment': 'adjustment.voucher'}


class PrintVoucherWizard(models.TransientModel):
    _name = 'print.voucher.wizard'

    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string="Doctype",
        readonly=True,
        default=lambda self: self._get_default_doctype(),
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
        report_name = DOCTYPE_REPORT_MAP.get(self.doctype, False)
        if not report_name:
            raise ValidationError(_('No form for for this Doctype'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
