# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountConfigSettings(models.Model):
    _inherit = 'account.config.settings'

    group_chartfields_invoice = fields.Boolean(
        'Chartfields on invoice line',
        implied_group='pabi_chartfield.group_invoice_chartfields',
        help="Allows you to add chartfields on invoice line.",
    )

    @api.onchange('group_chartfields_invoice')
    def onchange_chartfield(self):
        if self.group_chartfields_invoice:
            self.group_chartfields_invoice = True
        else:
            self.group_chartfields_invoice = False


class HRConfigSettings(models.Model):
    _inherit = 'hr.config.settings'

    group_chartfields_expense = fields.Boolean(
        'Chartfields on expense line',
        implied_group='pabi_chartfield.group_hr_expense_chartfields',
        help="Allows you to add chartfields on expense line.",
    )

    @api.onchange('group_chartfields_expense')
    def onchange_chartfield(self):
        if self.group_chartfields_expense:
            self.group_chartfields_expense = True
        else:
            self.group_chartfields_expense = False
