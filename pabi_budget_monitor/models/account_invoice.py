# -*- coding: utf-8 -*-

# TEMPORARY MOVED to account.py (account.move)

# from openerp import api, models
# from openerp.exceptions import ValidationError
#
#
# class AccountInvoice(models.Model):
#     _inherit = 'account.invoice'
#
#     @api.multi
#     def action_move_create(self):
#         res = super(AccountInvoice, self).action_move_create()
#         self._invoice_budget_check()
#         return res
#
#     @api.multi
#     def _invoice_budget_check(self):
#         Budget = self.env['account.budget']
#         for invoice in self:
#             if invoice.type != 'in_invoice':
#                 continue
#             doc_date = invoice.date_invoice
#             doc_lines = \
#                 Budget.convert_lines_to_doc_lines(invoice.invoice_line)
#             res = Budget.post_commit_budget_check(doc_date, doc_lines)
#             if not res['budget_ok']:
#                 raise ValidationError(res['message'])
#         return True
