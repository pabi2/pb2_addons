# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class SaleOrder(DoclineCommon, models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains('order_line')
    def _check_docline_seq(self):
        for order in self:
            self._compute_docline_seq('sale_order_line',
                                      'order_id', order.id)
        return True


class SaleOrderLine(DoclineCommonSeq, models.Model):
    _inherit = 'sale.order.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('sale.order').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,
                                       'sale_order',
                                       'sale_order_line',
                                       'order_id')
