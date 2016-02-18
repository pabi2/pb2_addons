# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        for inv in self:
            for line in inv.invoice_line:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
        res = super(AccountInvoice, self).action_move_create()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=False,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=False,
    )

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        self.product_id = False
        self.activity_group_id = self.activity_id.activity_group_id
        self.account_id = self.activity_id.account_id or \
            self.activity_id.activity_group_id.account_id

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        res['value'].update({'activity_group_id': False,
                             'activity_id': False, })
        return res
