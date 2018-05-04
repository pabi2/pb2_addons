# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class LoanCreatePaymentWizard(models.TransientModel):
    _name = 'loan.create.payment.wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        required=True,
    )
    installment_ids = fields.Many2many(
        'loan.installment.plan',
        string='Installment',
        domain=lambda self:
        [('reconcile_id', '=', False),
         ('loan_install_id', 'in', self._context.get('active_ids'))],
    )

    @api.model
    def default_get(self, field_list):
        res = super(LoanCreatePaymentWizard, self).default_get(field_list)
        loan_ids = self._context.get('active_ids', [])
        loans = self.env['loan.installment'].browse(loan_ids)
        self._validate(loans)
        res['partner_id'] = loans[0].partner_id.id
        return res

    @api.multi
    def _validate(self, loans):
        # Same partner
        partner_ids = list(set(loans.mapped('partner_id').ids))
        if len(partner_ids) > 1:
            raise ValidationError(
                _('Please select loan(s) from same partner!'))
        states = list(set(loans.mapped('state')))
        if len(states) != 1 or states[0] != 'open':
            raise ValidationError(_('Please select only opened loans(s)'))
        return True

    @api.multi
    def action_create_payment(self):
        self.ensure_one()
        loan_ids = self._context.get('active_ids', [])
        loans = self.env['loan.installment'].browse(loan_ids)
        _ids = self.installment_ids.ids
        res = loans.action_create_payment(installment_ids=_ids)
        res['context'].update({
            'default_partner_id': self.partner_id.id,
            'default_select': True,
            'default_date_value': fields.Date.context_today(self),
        })
        return res
