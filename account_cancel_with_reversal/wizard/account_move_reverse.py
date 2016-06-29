# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reverse"
    _description = "Create reversal of account moves"

    is_voucher = fields.Boolean(
        string='Voucher?',
    )
    is_invoice = fields.Boolean(
        string='Invoice?',
    )
    cancel_reason_txt = fields.Char(
        string="Reason",
        readonly=False,
    )

    @api.model
    def default_get(self, field_list):
        res = super(AccountMoveReversal, self).default_get(field_list)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        parent = self.env[model].browse(active_id)
        res['date'] = fields.Date.today()
        res['journal_id'] = parent.journal_id.id
        res['move_prefix'] = '_CANCELLED'
        return res

    @api.onchange('date')
    def _onchange_date(self):
        self.period_id = self.env['account.period'].find(self.date)[:1]

    @api.model
    def reconcile_reverse_journals(self, move_ids):
        account_move_line_obj = self.env['account.move.line']
        period_obj = self.env['account.period']
        date = time.strftime('%Y-%m-%d')
        ids = period_obj.find(dt=date)
        period_id = ids and ids[0] or False
        # Getting move_line_ids of the voided documents.
        self._cr.execute('select aml.id from account_move_line aml \
                        join account_account aa on aa.id = aml.account_id \
                        where aa.reconcile = true and aml.reconcile_id is null\
                        and aml.move_id in %s', (tuple(move_ids), ))
        move_line_ids = map(lambda x: x[0], self._cr.fetchall())

        move_line_ids = account_move_line_obj.browse(move_line_ids)
        line_dict = {}
        for line in move_line_ids:
            if line.account_id.id not in line_dict.keys():
                line_dict[line.account_id.id] = [line.id]
            else:
                line_dict[line.account_id.id].append(line.id)

        for account in line_dict.keys():
            move_line_ids = account_move_line_obj.browse(line_dict[account])
            move_line_ids.reconcile('manual', False,
                                    period_id, False)
#         move_line_ids.reconcile('manual', False,
#                                     period_id, False)

    @api.multi
    def action_reverse_invoice(self):
        assert 'active_ids' in self.env.context, "active_ids \
                                        missing in context"

        form = self.read()[0]
        period_id = form['period_id'][0] if form.get('period_id') else False
        journal_id = form['journal_id'][0] if form.get('journal_id') else False

        invoice_ids = self.env.context['active_ids']
        invoices = self.env['account.invoice'].browse(invoice_ids)
        reversed_move_ids = []
        for invoice in invoices:
            move_id = invoice.move_id
            reverse_move_id = move_id.create_reversals(
                form['date'],
                reversal_period_id=period_id,
                reversal_journal_id=journal_id,
                move_prefix=form['move_prefix'],
                move_line_prefix=form['move_line_prefix'],
                )
            invoice.write({'cancel_move_id': reverse_move_id[0],
                           'cancel_reason_txt': form['cancel_reason_txt'], })
            # cancel invoice
            invoice.signal_workflow('invoice_cancel')
            reversed_move_ids.extend(reverse_move_id)
            # reconcile new journal entry
            self.reconcile_reverse_journals([reverse_move_id[0], move_id.id])

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reverse_voucher(self):
        assert 'active_ids' in self.env.context, "active_ids\
                                                 missing in context"

        form = self.read()[0]

        period_id = form['period_id'][0] if form.get('period_id') else False
        journal_id = form['journal_id'][0] if form.get('journal_id') else False
        voucher_ids = self.env.context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(voucher_ids)
        reversed_move_ids = []
        for voucher in voucher_ids:
            # refresh to make sure you don't unlink an already removed move
            voucher.refresh()
            move_id = voucher.move_id
            reverse_move_id = move_id.create_reversals(
                form['date'],
                reversal_period_id=period_id,
                reversal_journal_id=journal_id,
                move_prefix=form['move_prefix'],
                move_line_prefix=form['move_line_prefix'],
                )
            voucher.write({'cancel_move_id': reverse_move_id[0],
                           'cancel_reason_txt': form['cancel_reason_txt'], })
            voucher.cancel_voucher()
            reversed_move_ids.extend(reverse_move_id)

            # reconcile new journal entry
            self.reconcile_reverse_journals([reverse_move_id[0], move_id.id])

        return {'type': 'ir.actions.act_window_close'}
