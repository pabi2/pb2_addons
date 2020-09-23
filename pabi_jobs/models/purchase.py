# -*- coding: utf-8 -*-
import logging
from openerp import models, api

_logger = logging.getLogger(__name__)

class JobPurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def action_pr_release_all_commited_budget(self, emps=[]):
        #_logger.info("--- > action_pr_release_all_commited_budget")
        print("--- > action_pr_release_all_commited_budget")
        self._cr.execute('SELECT AA.id , AA.document , AA.amount FROM s'
                            '(SELECT pr.id , pr.name AS document, SUM(aa.amount) AS amount'
                            'FROM issi_budget_summary_consume_view aa'
                            'LEFT JOIN purchase_request_line pr_line ON aa.purchase_request_line_id = pr_line.id'
                            'LEFT JOIN purchase_request pr ON pr_line.request_id = pr.id'
                            'WHERE aa.budget_commit_type <> ''actual'''
                            'AND aa.amount <> 0'
                            'AND aa.budget_commit_type =''pr_commit'''
                            'AND pr.technical_closed    IS TRUE'
                            'GROUP BY pr.id , pr.name'
                            ') AA WHERE AA.amount <> 0;')
        
        #lines = self.env['purchase.request'].browse([r[0] for r in self._cr.fetchall()])
        for r in self._cr.fetchall():
            print(r[0])
#         if self._cr.rowcount:
#             print(self._cr.fetchone()[0])
        return True
