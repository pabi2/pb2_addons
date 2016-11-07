# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('filter_by_invoice_ids'):
            _ids = self._context.get('filter_by_invoice_ids')
            args += [('invoice', 'in', _ids)]
        return super(AccountMoveLine, self).search(args, offset=offset,
                                                   limit=limit, order=order,
                                                   count=count)
