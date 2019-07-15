# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class PurchaseOrder(DoclineCommon, models.Model):
    _inherit = 'purchase.order'

    @api.multi
    @api.constrains('order_line')
    def _check_docline_seq(self):
        for order in self:
            self._compute_docline_seq('purchase_order_line','order_id',)
            
            ''' if self.state == 'draft'and self.order_line:
               search_this_id = self.env["purchase.order"].search([('id', '=', self.id)], limit=1)
               order_lines = search_this_id.order_line.ids
               line = search_this_id.order_line[len(order_lines)-1]
               print search_this_id,order_lines,line'''
                        
        return True
    
    @api.multi
    @api.onchange('order_line')
    def _check_orderline(self):
        for order in self:
            
            if self.state == 'draft'and self.order_line:
               search_this_id = self.env["purchase.order"].search([('id', '=', self.id)], limit=1)
               order_lines = search_this_id.order_line.ids
               line = search_this_id.order_line[len(order_lines)-1]
               print search_this_id, order_lines, line
               

class PurchaseOrderLine(DoclineCommonSeq, models.Model):
    _inherit = 'purchase.order.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('purchase.order').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,'purchase_order','purchase_order_line','order_id')  \
     
                      
    '''@api.multi
    @api.OnChange('order_line')
    def _check_docline_seq(self):
        for order in self:
            self._compute_docline_seq('purchase_order_line','order_id', order.id)
            
            
            if self.state == 'draft'and self.order_line:
               search_this_id = self.env["purchase.order"].search([('id', '=', self.id)], limit=1)
               order_lines = search_this_id.order_line.ids
               line = search_this_id.order_line[len(order_lines)-1]
               print search_this_id,order_lines,line
                    
            
        return True'''