# -*- coding: utf-8 -*-
from openerp import api, models, fields
from .chartfield import ChartFieldAction, HeaderTaxBranch


class HRExpenseExpense(HeaderTaxBranch, models.Model):
    _inherit = 'hr.expense.expense'

    taxbranch_id = fields.Many2one(
        compute='_compute_taxbranch_id',
        store=True,
    )

    @api.one
    @api.depends('line_ids')
    def _compute_taxbranch_id(self):
        lines = self.line_ids
        self.taxbranch_id = self._check_taxbranch_id(lines)


class HRExpenseLine(ChartFieldAction, models.Model):
    _inherit = 'hr.expense.line'

    @api.model
    def create(self, vals):
        res = super(HRExpenseLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
