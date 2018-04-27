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
