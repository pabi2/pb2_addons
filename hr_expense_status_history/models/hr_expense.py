# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    expense_auditlog_line_ids = fields.Many2many(
        'document.auditlog.log.line',
        compute='_compute_log_lines',
        string="Expense Status History"
    )

    @api.depends()
    def _compute_log_lines(self):
        for record in self:
            self._cr.execute("""
                SELECT logline.id
                FROM
                    document_auditlog_log_line logline
                JOIN ir_model as model
                    ON (model.id = logline.model_id)
                WHERE model.model = '%s' AND
                    logline.res_id = %d
            """ % (self._model, record.id))
            result = self._cr.fetchall()
            line_ids = [r[0] for r in result]
            record.expense_auditlog_line_ids = [(6, 0, line_ids)]
