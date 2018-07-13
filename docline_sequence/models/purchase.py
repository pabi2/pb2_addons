# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class PurchaseOrder(DoclineCommon, models.Model):
    _inherit = 'purchase.order'

    @api.multi
    @api.constrains('order_line')
    def _check_docline_seq(self):
        for order in self:
            self._compute_docline_seq('purchase_order_line',
                                      'order_id', order.id)
        return True


class PurchaseOrderLine(DoclineCommonSeq, models.Model):
    _inherit = 'purchase.order.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('purchase.order').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,
                                       'purchase_order',
                                       'purchase_order_line',
                                       'order_id')
