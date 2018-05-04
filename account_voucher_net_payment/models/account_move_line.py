# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _prepare_net_args(self, args, account_type):
        net_args = [x for x in args if x[0] != 'account_id.type']
        net_args.append(('account_id.type', '=', account_type))
        return net_args

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_net_payment = self._context.get('allow_net_payment')
        if allow_net_payment:
            dom_type = [x for x in args if x[0] == 'account_id.type']
            if dom_type:
                account_type = (dom_type[0][2] == 'payable' and
                                'receivable' or 'payable')
                net_args = self._prepare_net_args(args, account_type)
                net_move_line_ids = \
                    self.with_context(allow_net_payment=False,
                                      filter_invoices=[]).\
                    search(net_args)
                # Add move_line_ids form the opposite side with OR operator
                x_args = []
                for arg in args:
                    x_args.append('&')
                    x_args.append(arg)
                args = ['|', ('id', 'in', net_move_line_ids._ids)] + x_args
        return super(AccountMoveLine, self).search(args, offset=offset,
                                                   limit=limit, order=order,
                                                   count=count)
