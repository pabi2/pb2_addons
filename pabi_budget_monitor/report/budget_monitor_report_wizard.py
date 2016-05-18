# -*- coding: utf-8 -*-
from openerp import api, fields, models


class BudgetMonitorReportWizard(models.TransientModel):
    _name = 'budget.monitor.report.wizard'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )


#     <record id="action_budget_monitor_report" model="ir.actions.act_window">
#         <field name="name">Budget Monitor</field>
#         <field name="res_model">budget.monitor.report</field>
#         <field name="view_type">form</field>
#         <field name="view_mode">tree,graph</field>
#         <field name="context">{}</field>
#         <field name="search_view_id" ref="view_budget_monitor_report_search"/>
#         <field name="help">From this report, you can have an budget overview of Commitment vs Actual</field>
# 
#     </record>


    @api.multi
    def open_report(self):
        self.ensure_one()
        action = self.env.ref('account_budget_activity.'
                              'action_budget_monitor_report')
        result = action.read()[0]
#         print result
#         x = 1/0
#         result['views'] = [(False, 'form')]
#         result['res_id'] = move_id

#         print action.res_model
#         res = {
#             'type': 'ir.actions.act_window',
#             'name': action.name,
#             'res_model': action.res_model,
#             'view_type': action.view_type,
#             'view_mode': 'graph,tree',
#             'context': {},
#             'domain': [],
#         }
        print result
        return result
