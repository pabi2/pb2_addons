# -*- coding: utf-8 -*-
import logging
import datetime

from openerp import models, api

_logger = logging.getLogger(__name__)

class AcctionReleaseAllCommited(models.Model):
    _inherit = 'account.budget'

    @api.multi
    def action_hook_release_all_committed_budget(self,model):
        vals = False
        # PR
        if model == 'purchase.request':
            self._cr.execute("""
                    SELECT * FROM (SELECT  AA.id , AA.document , AA.amount FROM 
                    (SELECT  pr.id , pr.name AS document , SUM(aa.amount) AS amount
                    FROM issi_budget_summary_consume_view aa
                    LEFT JOIN purchase_request_line pr_line ON aa.purchase_request_line_id = pr_line.id
                    LEFT JOIN purchase_request pr ON pr_line.request_id = pr.id
                    WHERE aa.budget_commit_type <> 'actual'
                    AND aa.amount <> 0
                    AND aa.budget_commit_type = 'pr_commit'
                    AND pr.technical_closed    IS TRUE
                    GROUP BY pr.id , pr.name
                    ) AA
                    UNION
                    SELECT AA.id , AA.document , AA.amount 
                    FROM ( SELECT  pr.id , pr.name AS document , SUM(aa.amount) AS amount
                    FROM issi_budget_summary_consume_view aa
                    LEFT JOIN purchase_request_line pr_line ON aa.purchase_request_line_id = pr_line.id
                    LEFT JOIN purchase_request pr ON pr_line.request_id = pr.id
                    LEFT JOIN purchase_request_purchase_requisition_line_rel prpd_rel ON aa.purchase_request_line_id = prpd_rel.purchase_request_line_id
                    LEFT JOIN purchase_requisition_line prpd_line ON prpd_rel.purchase_requisition_line_id = prpd_line.id
                    LEFT JOIN purchase_requisition prpd ON prpd_line.requisition_id = prpd.id
                    LEFT JOIN purchase_order popd ON prpd.id = popd.requisition_id
                    WHERE aa.budget_commit_type <> 'actual'
                    AND aa.amount <> 0
                    AND aa.budget_commit_type = 'pr_commit'
                    AND popd.state IN('accepted','confirm','done')
                    AND pr.technical_closed    IS NOT TRUE
                    AND LEFT(popd.name,2) = 'PO'
                    GROUP BY pr.id , pr.name) AA ) xx WHERE xx.amount<>0;""") 
            vals = self._cr.dictfetchall() 
 
        # EX
        elif model == 'hr.expense.expense':
            self._cr.execute("""
                    SELECT * FROM (
                    SELECT  ex.id , ex.number AS document , SUM(aa.amount) AS amount
                    FROM issi_budget_summary_consume_view aa
                    LEFT JOIN hr_expense_line line ON aa.expense_line_id = line.id
                    LEFT JOIN hr_expense_expense ex ON line.expense_id = ex.id
                    WHERE aa.budget_commit_type <> 'actual'
                    AND aa.amount <> 0
                    AND aa.budget_commit_type = 'exp_commit'
                    AND ex.technical_closed    IS TRUE
                    AND LEFT(ex.number,2)= 'EX'
                    GROUP BY ex.id , ex.number
                    UNION
                    SELECT  ex.id , ex.number AS document , SUM(aa.amount) AS amount
                    FROM issi_budget_summary_consume_view aa
                    LEFT JOIN hr_expense_line line ON aa.expense_line_id = line.id
                    LEFT JOIN hr_expense_expense ex ON line.expense_id = ex.id
                    WHERE aa.budget_commit_type <> 'actual'
                    AND aa.amount <> 0
                    AND aa.budget_commit_type = 'exp_commit'
                    AND ex.state = 'paid'
                    AND LEFT(ex.number,2)= 'EX'
                    GROUP BY ex.id , ex.number
                    ) xx WHERE xx.amount<>0;""")
            
            vals = self._cr.dictfetchall()  
    
        if vals: 
            for x in vals:
                obj = self.env[model].search([('id','=',x['id'])])
                obj.release_all_committed_budget()
#                 print(u'RELEASE COMMIT - %s', obj.display_name)
                _logger.info("Hook Release Committed '%s'.", obj.display_name)
                                
        return True
