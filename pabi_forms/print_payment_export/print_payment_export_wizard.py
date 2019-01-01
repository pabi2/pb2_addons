# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class PrintPaymentExportWizard(models.TransientModel):
    _name = 'print.payment.export.wizard'

    report = fields.Selection(
        [('payment.export.form', 'Payment Export'),
         ('cheque.form', 'Cheque')],
        string='Report',
        readonly=False,
        default=lambda self: self._get_default_report(),
    )

    @api.model
    def _get_default_report(self):
        active_ids = self._context.get('active_ids')
        exports = self.env['payment.export'].browse(active_ids)
        ttypes = list(set(exports.mapped('payment_type')))
        if len(ttypes) > 1:
            raise ValidationError(
                _('Not allow mixing tranfer and cheque'))
        ttype = ttypes[0]
        report = ttype == 'transfer' and 'payment.export.form' or 'cheque.form'
        return report

    @api.multi
    def action_print_payment_export(self):
        data = {'parameters': {}}
        ids = self._context.get('active_ids')
        data['parameters']['ids'] = ids
        report_name = self.report
        if not report_name:
            raise ValidationError(_('No form for for this report type'))
        if report_name == 'payment.export.form':
            exports = self.env['payment.export'].browse(ids)
            if False in exports.mapped('exported'):
                raise ValidationError(_('Payment is not packed yet!'))
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': self._context,  # Requried for report wizard
        }
        return res
