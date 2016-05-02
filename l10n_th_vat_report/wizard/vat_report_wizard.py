# -*- coding: utf-8 -*-

from openerp import fields, models, api


class AccountVatReport(models.TransientModel):
    _name = 'account.vat.report'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        required=True,
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
        required=True,
    )
    base_code_id = fields.Many2one(
        'account.tax.code',
        string='Base Code',
        required=True,
    )
    tax_code_id = fields.Many2one(
        'account.tax.code',
        string='Tax Code',
        required=True,
    )

    @api.onchange('tax_id')
    def onchange_tax(self):
        for wizard in self:
            wizard.base_code_id = wizard.tax_id.base_code_id.id
            wizard.tax_code_id = wizard.tax_id.tax_code_id.id

    @api.multi
    def print_report(self):
        data = self.read([])[0]
        return self.env['report'].get_action(
            self, 'l10n_th_vat_report.report_vat', data=data)
