# -*- coding: utf-8 -*-
from openerp import api, models, fields
from .chartfield import ChartFieldAction, HeaderTaxBranch


class HRExpenseExpense(HeaderTaxBranch, models.Model):
    _inherit = 'hr.expense.expense'

    taxbranch_ids = fields.Many2many(
        compute='_compute_taxbranch_ids',
    )
    len_taxbranch = fields.Integer(
        compute='_compute_taxbranch_ids',
    )

    @api.one
    @api.depends('line_ids')
    def _compute_taxbranch_ids(self):
        lines = self.line_ids
        self._set_taxbranch_ids(lines)

    @api.model
    def create(self, vals):
        res = super(HRExpenseExpense, self).create(vals)
        res._set_header_taxbranch_id()
        return res


class HRExpenseLine(ChartFieldAction, models.Model):
    _inherit = 'hr.expense.line'

    @api.model
    def create(self, vals):
        res = super(HRExpenseLine, self).create(vals)
        res.update_related_dimension(vals)
        return res
