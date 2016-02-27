# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import \
    models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField


class CrossoveredBudgetLines(ChartField, models.Model):
    _inherit = 'crossovered.budget.lines'

    display_name = fields.Char(
        string='Display Name',
        readonly=True,
        compute='_compute_display_name',
    )

    @api.multi
    @api.depends()
    def _compute_display_name(self):
        for rec in self:
            if rec.activity_id:
                rec.display_name = rec.activity_id.name
                continue
            if rec.activity_group_id:
                rec.display_name = rec.activity_group_id.name
                continue
            for chartfield in CHART_FIELDS:
                if rec[chartfield[0]]:
                    rec.display_name = rec[chartfield[0]].name
                    break
