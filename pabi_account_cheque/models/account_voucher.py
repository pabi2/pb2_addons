# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(AccountVoucher, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        context = self._context.copy()
        module = 'pabi_account_cheque'
        bbl_cheque_ref = self.env.ref(
            module + '.' + 'supplier_payment_bbl_cheque').id
        ktb_cheque_ref = self.env.ref(
            module + '.' + 'supplier_payment_ktb_cheque').id
        reports = []
        for report in res.get('toolbar', {}).get('print', []):
            if report.get('id', False) in [bbl_cheque_ref, ktb_cheque_ref]:
                if context.get('type', False) == 'payment':
                    reports.append(report)
            else:
                reports.append(report)
        if res.get('toolbar', {}).get('print', False):
            res['toolbar']['print'] = reports
        return res
