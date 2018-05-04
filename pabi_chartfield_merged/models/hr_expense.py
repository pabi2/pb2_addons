# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError
from .chartfield import MergedChartField


class HRExpenseLine(MergedChartField, models.Model):
    _inherit = 'hr.expense.line'

    @api.multi
    def write(self, vals):
        if vals.get('chartfield_id', False):
            raise ValidationError(
                _('Changing budget field is not allowed,\n'
                  'budget was commit during document creation'))
        return super(HRExpenseLine, self).write(vals)
