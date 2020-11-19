# -*- coding: utf-8 -*-
import logging
import datetime

from openerp import models, api

_logger = logging.getLogger(__name__)

class AcctionRecomputeAdjust(models.Model):
    _inherit = 'account.move'

    @api.multi
    def action_recompute_adjust(self):
        
        vals = False
        self._cr.execute("""
                SELECT DISTINCT mv.id , mv.name 
                FROM account_move mv
                LEFT JOIN account_move_line mvl ON mv.id = mvl.move_id
                LEFT OUTER JOIN account_analytic_line al ON al.move_id = mvl.id
                WHERE LEFT(mv.name,8) = 'JV200000'
                AND al.document IS NULL
                AND al.id IS NOT NULL;""") 
        vals = self._cr.dictfetchall()
    
        if vals: 
            for x in vals:
                obj = self.search([('id','=',x['id'])])
                obj._compute_document_analytic_line()
#                 print(u'Recompute Adjust - %s', obj.name)
                _logger.info("Recompute Adjust - '%s'", obj.display_name)
                                
        return True
