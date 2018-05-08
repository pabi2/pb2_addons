# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

CHEQUE_REPORT_MAP = {
    'bay_cheque': 'supplier.payment.bay.cheque',
    'bbl_cheque': 'supplier.payment.bbl.cheque',
    'ktb_cheque': 'supplier.payment.ktb.cheque',
    'scb_cheque': 'supplier.payment.scb.cheque',
}


class PrintPaymentChequeWizard(models.TransientModel):
    _name = 'print.payment.cheque.wizard'

    bank_print = fields.Selection(
        selection='_get_voucher_bank_cheque',
        string="Bank Cheque",
        required=True,
    )

    @api.multi
    def action_print_payment_cheque(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        try:
            report_name = CHEQUE_REPORT_MAP.get(self.bank_print, False)
        except Exception:
            raise ValidationError(_('No form for for this Cheque'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res

    @api.model
    def _get_voucher_bank_cheque(self):
        ids = self._context.get('active_ids')
        if ids:
            voucher = self.env['account.voucher'].browse(ids[0])
            if voucher.type == 'receipt':
                return []
            elif voucher.type == 'payment':
                return [
                    ('bay_cheque', 'Bay Cheque'),
                    ('bbl_cheque', 'BBL Cheque'),
                    ('ktb_cheque', 'KTB Cheque'),
                    ('scb_cheque', 'SCB Cheque'),
                ]
        return []
