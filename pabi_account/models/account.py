# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    line_item_summary = fields.Text(
        string='Items Summary',
        compute='_compute_line_item_summary',
        store=True,
        help="This field provide summary of items in move line with Qty."
    )

    @api.multi
    def _write(self, vals):
        if 'line_item_summary' in vals:
            self._write({'narration': vals.get('line_item_summary', False)})
        return super(AccountMove, self)._write(vals)

    @api.multi
    @api.depends('line_id.name')
    def _compute_line_item_summary(self):
        for rec in self:
            items = ['%s [%s]' % (x.name, x.quantity)
                     for x in rec.line_id
                     if (x.name != '/' and
                         x.account_id.user_type.report_type in ('income',
                                                                'expense'))]
            rec.line_item_summary = ", ".join(items)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        # Option to filter only company's bank's account
        if self._context.get('company_bank_account_only', False):
            BankAcct = self.env['res.partner.bank']
            banks = BankAcct.search([
                ('state', '=', 'SA'),  # Only Saving Bank Account
                ('partner_id', '=', self.env.user.company_id.partner_id.id)])
            account_ids = banks.mapped('journal_id').\
                mapped('default_debit_account_id').ids
            args += [('id', 'in', account_ids)]
        return super(AccountAccount, self).name_search(name=name,
                                                       args=args,
                                                       operator=operator,
                                                       limit=limit)
