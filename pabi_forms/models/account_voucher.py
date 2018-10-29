# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    # For reporting purpose only
    line_ids_name = fields.Text(
        compute='_compute_line_ids',
    )
    line_ids_amount = fields.Text(
        compute='_compute_line_ids',
    )
    # --
    # For Receipt for Supplier forms
    wa_total_fine = fields.Float(
        string='WA Total Fine',
        compute='_compute_wa_total_fine',
    )
    wa_voucher_diff_comment = fields.Char(
        string='WA Diff Comment',
        compute='_compute_wa_total_fine',
    )
    retention_amount = fields.Float(
        string='Retention Amount',
        compute='_compute_retention_amount',
    )

    @api.multi
    def _compute_line_ids(self):
        for rec in self:
            lines = rec.line_ids.sorted(key=lambda l: l.move_line_id.name)
            invoices = lines.mapped('invoice_id')
            amounts = lines.mapped('amount')
            amounts = ['{:,.2f}'.format(amount) for amount in amounts]
            rec.line_ids_name = '\n'.join(invoices.mapped('number'))
            rec.line_ids_amount = '\n'.join(amounts)

    def filter_print_report(self, res, reports):
        action = []
        if res.get('toolbar', False) and \
                res.get('toolbar').get('print', False):
            for act in res.get('toolbar').get('print'):
                if act.get('name') in reports:
                    action.append(act)
            res['toolbar']['print'] = action
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
        # Customer Payment
        # if self._context.get('type', False) == 'receipt':
        #     reports = [
        #         u'Customer/Payment',
        #     ]
        #     self.filter_print_report(res, reports)
        # Customer Receipt
        if self._context.get('type', False) == 'sale' and\
                self._context.get('default_type', False) == 'sale':
            reports = []
            self.filter_print_report(res, reports)
        # Suplier Payment
        elif self._context.get('type', False) == 'payment':
            reports = [
                u'Print Cheque',
                u'Print Receipt',
            ]
            self.filter_print_report(res, reports)
        # Customer Receipt
        elif self._context.get('type', False) == 'purchase' and\
                self._context.get('default_type', False) == 'purchase':
            reports = []
            self.filter_print_report(res, reports)
        return res

    # For customer/supplier receipt report
    @api.multi
    def _compute_wa_total_fine(self):
        company = self.env.user.company_id
        for rec in self:
            # from invoice
            amount_from_invoice = abs(sum(rec.line_ids.mapped(
                'invoice_id.late_delivery_work_acceptance_id.total_fine')))
            # form payment diff
            accounts = [company.delivery_penalty_activity_id.account_id.id]
            diff_lines = rec.multiple_reconcile_ids.\
                filtered(lambda l: l.account_id.id in accounts)
            amount_from_diff = abs(sum(diff_lines.mapped('amount')))
            rec.wa_total_fine = amount_from_invoice + amount_from_diff
            comment_from_diff = ', '.join(diff_lines.mapped('note'))
            rec.wa_voucher_diff_comment = comment_from_diff
        return True

    @api.multi
    def _compute_retention_amount(self):
        company = self.env.user.company_id
        for rec in self:
            # from invoice
            amount_from_invoice = abs(sum(
                rec.line_ids.mapped('invoice_id').
                filtered('is_retention_return').  # Get only with PO retention
                mapped('amount_total'))) or 0.0
            # from voucher line retention
            amount_from_voucher = \
                abs(sum(rec.line_ids.mapped('amount_retention'))) or 0.0
            # from payment diff
            accounts = company.account_retention_customer_ids.ids + \
                company.account_retention_supplier_ids.ids
            amount_from_diff = abs(sum(
                rec.multiple_reconcile_ids.
                filtered(lambda l: l.account_id.id in accounts).
                mapped('amount'))) or 0.0
            rec.retention_amount = amount_from_invoice + \
                amount_from_voucher + amount_from_diff
        return True
