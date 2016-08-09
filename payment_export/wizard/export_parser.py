# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class PaymentExportParser(models.TransientModel):
    _inherit = 'payment.export.parser'
    _description = 'Export Payment'

    @api.multi
    def export_file(self):
        res = super(PaymentExportParser, self).export_file()
        if res:
            self.ensure_one()
            payment_export_id = self.env.context.get('active_id', False)
            payment_export_model = self.env.context.get('active_model', '')
            export = self.env[payment_export_model].browse(payment_export_id)
            export.action_done()
        return res
