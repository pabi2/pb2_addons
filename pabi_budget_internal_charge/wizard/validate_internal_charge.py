# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class ValidateInternalCharge(models.TransientModel):
    _name = 'validate.internal.charge'

    @api.multi
    def validate_internal_charge(self):
        self.ensure_one()
        ExLine = self.env['hr.expense.line']
        active_ids = self._context.get('active_ids')
        exp_lines = ExLine.browse(active_ids)
        expenses = exp_lines.mapped('expense_id')
        # Only draft expenses can be validated
        non_drafts = \
            expenses.filtered(lambda l: l.state != 'draft').mapped('number')
        if non_drafts:
            raise ValidationError(
                _('Following expenses can not be validated '
                  '(non-draft).\n%s') % ', '.join(non_drafts))
        # All line of expense must have inrev_activity
        invalid_lines = ExLine.search([('expense_id', 'in', expenses.ids),
                                       ('inrev_activity_id', '=', False)])
        invalid_ex = []
        if invalid_lines:
            invalid_ex = invalid_lines.mapped('expense_id').mapped('number')
        if invalid_ex:
            raise ValidationError(
                _('Following expenses, not all of its lines have revenue '
                  'activity selected\n%s') % ', '.join(invalid_ex))
        for expense in expenses:
            expense.signal_workflow('internal_charge')
