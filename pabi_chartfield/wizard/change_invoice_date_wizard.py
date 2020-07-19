# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import datetime

class ChangeDateValue(models.TransientModel):
    _name = 'change.invoice.date'
    
    reason = fields.Char(
        string="Reason",
        required=True,
        size=500,
    )
    invoice_date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    
    @api.multi
    def action_change_invoice_date(self):
        sale_ids = self._context.get('active_ids', [])
        sale_ids = self.env['sale.order'].browse(sale_ids)
        for sale in sale_ids:
            sale.reason = self.reason
            for invoice in sale.invoice_plan_ids:
                if invoice.state == 'draft':
                    invoice.date_invoice = self.invoice_date
            for inv in sale.invoice_ids:
                if inv.state == 'draft':
                    inv.date_invoice = self.invoice_date
                    inv.date_document = self.invoice_date
                    