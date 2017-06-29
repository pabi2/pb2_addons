# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    def action_date_assign(self):
        """ Only when date due is not specified. Use system suggestion """
        if not self.date_due:
            super(AccountInvoice, self).action_date_assign()
        return True
