# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _

OVERDUE_DAYS = {'l1': 7, 'l2': 14, 'l3': 19}


class PABIPartnerDunningWizard(models.TransientModel):
    _name = 'pabi.partner.dunning.wizard'

    date_run = fields.Date(
        string='Report Run Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    report_type = fields.Selection(
        [('l1', 'Overdue 7 Days'),
         ('l2', 'Overdue 14 Days'),
         ('l3', 'Overdue 19 Days')],
        string='Type',
        default='l1',
    )
    show_no_stamp = fields.Boolean(
        string='Show No-Stamped Only',
        default=True,
    )
    account_type = fields.Selection(
        [('payable', 'Payable'),
         ('receivable', 'Receivable')],
        string='Account Type',
        required=True,
        default='receivable',
    )
    open_item = fields.Boolean(
        string='Unpaid Items Only',
        default=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    groupby_org = fields.Boolean(
        string='Org',
        default=False,
    )
    groupby_partner = fields.Boolean(
        string='Partner',
        default=False,
    )

    @api.model
    def _get_filter(self):
        Report = self.env['pabi.partner.dunning.report']
        domain = []
        if self.account_type:
            domain.append(('account_type', '=', self.account_type))
        if self.report_type:
            days = OVERDUE_DAYS[self.report_type]
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
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        return domain

    @api.model
    def _get_groupby(self):
        res = {}
        if self.groupby_org:
            res.update({'search_default_groupby_org': True})
        if self.groupby_partner:
            res.update({'search_default_groupby_partner': True})
        return res

    @api.multi
    def run_report(self):
        self.ensure_one()
        action = self.env.ref('pabi_partner_dunning_report.'
                              'action_pabi_partner_dunning_report')
        result = action.read()[0]
        # Get filter
        domain = []
        domain += self._get_filter()
        result.update({'domain': domain})
        # Group by
        result['context'] = {'date_run': self.date_run}
        result['context'].update(self._get_groupby())
        # Update report name
        report_name = self.report_type and \
            _('%s Days Overdue') % (OVERDUE_DAYS[self.report_type]) or \
            _('- Days Overdue')
        result.update({'display_name': report_name})
        result.update({'name': report_name})
        return result
