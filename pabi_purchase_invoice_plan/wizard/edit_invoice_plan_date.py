# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class EditInvoicePlanDate(models.TransientModel):
    _name = 'edit.invoice.plan.date'

    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditInvoicePlanDate, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        line = self.env[active_model].browse(active_id)
        res['date_invoice'] = line.date_invoice
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        line = self.env[active_model].browse(active_id)
        if line.ref_invoice_id.state == 'draft':
            line.write({'date_invoice': self.date_invoice})
            # Use date document
            line.ref_invoice_id.write({'date_document': self.date_invoice})
        else:
            raise ValidationError(
                _('Only invoice in draft state is allowed to change date.'))
        return True
