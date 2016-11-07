# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class InovicesCreatePaymentWizard(models.TransientModel):
    _name = 'invoices.create.payment.wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(InovicesCreatePaymentWizard, self).default_get(field_list)
        invoice_ids = self._context.get('active_ids', [])
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self._validate(invoices)
        res['partner_id'] = invoices[0].partner_id.id
        return res

    @api.multi
    def _validate(self, invoices):
        # Same partner
        partner_ids = list(set(invoices.mapped('partner_id').ids))
        if len(partner_ids) > 1:
            raise UserError(_('Please select invoice(s) from same partner!'))
        states = list(set(invoices.mapped('state')))
        if len(states) != 1 or states[0] != 'open':
            raise UserError(_('Please select only Open invoice(s)'))
        return True

    @api.multi
    def action_create_payment(self):
        self.ensure_one()
        invoice_ids = self._context.get('active_ids', [])
        invoices = self.env['account.invoice'].browse(invoice_ids)
        res = invoices.action_create_payment()
        res['context'].update({
            'default_partner_id': self.partner_id.id,
            'default_select': True,
        })
        return res
