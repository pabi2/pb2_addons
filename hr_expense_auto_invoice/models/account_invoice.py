# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import except_orm


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def confirm_paid(self):
        expenses = self.env['hr.expense.expense'].search([('invoice_id',
                                                           'in', self._ids)])
        if expenses:
            expenses.write({'state': 'paid'})
        return super(AccountInvoice, self).confirm_paid()

    @api.multi
    def action_cancel(self):
        expenses = self.env['hr.expense.expense'].search([('invoice_id',
                                                           'in', self._ids)])
        if expenses:
            expenses.signal_workflow('done_to_refuse')
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def invoice_validate(self):
        expenses = self.env['hr.expense.expense'].search([('invoice_id',
                                                           'in', self._ids)])
        for expense in expenses:
            if expense.amount != expense.invoice_id.amount_total:
                raise except_orm(
                    _('Amount Error!'),
                    _("This invoice amount is not equal to amount in "
                      "expense: %s" % (expense.number,)))
            expense.signal_workflow('refuse_to_done')
        return super(AccountInvoice, self).invoice_validate()
