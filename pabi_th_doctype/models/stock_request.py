# -*- coding: utf-8 -*-
from openerp import models, api

_DOCTYPE = {'request': 'stock_request',
            'borrow': 'stock_borrow',
            'transfer': 'stock_transfer'}


class StockRequest(models.Model):
    _inherit = 'stock.request'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = _DOCTYPE.get(self._context.get('default_type'))
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        return super(StockRequest, self).create(vals)
