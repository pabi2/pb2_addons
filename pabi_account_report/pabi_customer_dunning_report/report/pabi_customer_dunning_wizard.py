# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _


class PABICustomerDunningWizard(models.TransientModel):
    _name = 'pabi.customer.dunning.wizard'

    date_run = fields.Date(
        string='Report Run Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    report_type = fields.Selection(
        [('7', 'Overdue 7 Days'),
         ('14', 'Overdue 14 Days'),
         ('19', 'Overdue 19 Days')],
        string='Type',
        default='7',
    )
    open_item = fields.Boolean(
        string='Unpaid Items Only',
        default=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    groupby_org = fields.Boolean(
        string='Org',
        default=False,
    )

    @api.model
    def _get_filter(self):
        Report = self.env['pabi.customer.dunning.report']
        domain = []
        if self.report_type:
            days = int(self.report_type)
            date_due = (datetime.strptime(self.date_run, '%Y-%m-%d') -
                        relativedelta(days=days)).strftime('%Y-%m-%d')
            _ids = Report.search([('date_maturity', '=', date_due)])._ids
            domain.append(('move_line_id', 'in', _ids))
        else:
            _ids = Report.search([('date_maturity', '<', self.date_run)])._ids
            domain.append(('move_line_id', 'in', _ids))
        if self.open_item:
            domain.append(('reconcile_id', '=', False))
        if self.org_id:
            domain.append(('org_id', '=', self.org_id.id))
        return domain

    @api.model
    def _get_groupby(self):
        res = {}
        if self.groupby_org:
            res.update({'search_default_groupby_org': True})
        return res

    @api.multi
    def run_report(self):
        self.ensure_one()
        action = self.env.ref('pabi_account_report.'
                              'action_pabi_customer_dunning_report')
        result = action.read()[0]
        # Get filter
        domain = []
        domain += self._get_filter()
        result.update({'domain': domain})
        # Group by
        result['context'] = {'date_run': self.date_run}
        result['context'].update(self._get_groupby())
        # Update report name
        report_name = _('Customer Dunning Report - %s Days Overdue') % \
            (self.report_type)
        result.update({'display_name': report_name})
        result.update({'name': report_name})
        return result
