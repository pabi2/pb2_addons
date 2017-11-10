# -*- coding: utf-8 -*-
from openerp import models, fields, api

SEARCH_OPTIONS = [
    ('today_dunning_report', 'Today Dunning Report'),
    ('printed_report', 'Printed Report'),
]


class SearchPartnerDunningReportWizard(models.TransientModel):
    _name = 'search.partner.dunning.report.wizard'

    search_options = fields.Selection(
        selection=SEARCH_OPTIONS,
        string='Search',
        required=True,
        default='today_dunning_report',
    )

    @api.model
    def _get_domain(self):
        Report = self.env['pabi.partner.dunning.report']
        date_run = fields.Date.context_today(self)
        domain = [('reconcile_id', '=', False),
                  ('account_type', '=', 'receivable')]
        _ids = Report.search([('date_maturity', '<=', date_run)])._ids
        domain.append(('move_line_id', 'in', _ids))

        # Search options
        if self.search_options == 'today_dunning_report':
            domain += ['|', ('l1_date', '=', date_run),
                       '|', ('l2_date', '=', date_run),
                       ('l3_date', '=', date_run)]
        else:
            domain += [('l1', '=', True), ('l2', '=', True), ('l3', '=', True)]
        return domain

    @api.multi
    def action_search_partner_dunning_report(self):
        action = self.env.ref('pabi_partner_dunning_report.'
                              'action_pabi_partner_dunning_report')
        result = action.read()[0]
        result.update({'domain': self._get_domain()})
        result.update({'context': {}})
        return result
