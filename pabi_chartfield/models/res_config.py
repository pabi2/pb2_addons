# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountConfigSettings(models.TransientModel):
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


class HRConfigSettings(models.TransientModel):
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


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    group_chartfields_purchase = fields.Boolean(
        'Chartfields on purchase order line',
        implied_group='pabi_chartfield.group_purchase_chartfields',
        help="Allows you to add chartfields on purchase order line.",
    )

    @api.onchange('group_chartfields_purchase')
    def onchange_chartfield(self):
        if self.group_chartfields_purchase:
            self.group_chartfields_purchase = True
        else:
            self.group_chartfields_purchase = False
