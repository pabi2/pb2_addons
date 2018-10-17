# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class PurchaseRequest(DoclineCommon, models.Model):
    _inherit = 'purchase.request'

    @api.multi
    @api.constrains('line_ids')
    def _check_docline_seq(self):
        for order in self:
            self._compute_docline_seq('purchase_request_line',
                                      'request_id', order.id)
        return True


class PurchaseRequestLine(DoclineCommonSeq, models.Model):
    _inherit = 'purchase.request.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('purchase.request').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,
                                       'purchase_request',
                                       'purchase_request_line',
                                       'request_id')
