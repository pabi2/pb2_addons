# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class JasperReportAssetInactiveOwner(models.TransientModel):
    _name = 'jasper.report.asset.inactive.owner'
    _inherit = 'report.account.common'
    
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        domain=[('state', '=', 'draft')],
        required=True,
        default=lambda self: self.env['account.period.calendar'].find()
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        if self.calendar_period_id:
#             dom += [('date', '>=', self.period_start_id.date_start)]
            date_start = self.calendar_period_id.date_start
        if self.calendar_period_id:
#             dom += [('date', '<=', self.period_end_id.date_stop)]
            date_end = self.calendar_period_id.date_stop
        return date_start,date_end
            
    @api.multi
    def start_report(self):
        self.ensure_one()
        date_start,date_end = self._compute_results()
        params = {}
        params['date_start'] = date_start
        params['date_end'] = date_end
        return { 
            'type': 'ir.actions.report.xml',
            'report_name': 'report_asset_inactive_owner',
            'datas': params,
        }  
