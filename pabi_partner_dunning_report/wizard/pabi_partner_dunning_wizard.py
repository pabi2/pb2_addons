# -*- coding: utf-8 -*-
from openerp import api, fields, models


class PABIPartnerDunningWizard(models.TransientModel):
    _name = 'pabi.partner.dunning.wizard'

    date_run = fields.Date(
        string='Report Run Date',
        readonly=True,
        default=lambda self: fields.Date.context_today(self),
        help="Always run as today"
    )

    @api.model
    def _get_domain(self):
        Report = self.env['pabi.partner.dunning.report']
        date_run = fields.Date.context_today(self)
        domain = [('reconcile_id', '=', False),
                  ('account_type', '=', 'receivable')]
        _ids = Report.search([('date_maturity', '<=', date_run)])._ids
        domain.append(('move_line_id', 'in', _ids))
        return domain

    @api.multi
    def run_report(self):
        self.ensure_one()
        action = self.env.ref('pabi_partner_dunning_report.'
                              'action_pabi_partner_dunning_report')
        result = action.read()[0]
        # Get domain
        domain = self._get_domain()
        result.update({'domain': domain})
        return result
