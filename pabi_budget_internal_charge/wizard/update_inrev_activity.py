# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class UpdateInrevActivity(models.TransientModel):
    _name = 'update.inrev.activity'

    inrev_activity_id = fields.Many2one(
        'account.activity',
        string='Internal Revenue Activity',
        required=True,
        domain=lambda self: self._inrev_activity_domain(),
    )

    @api.model
    def _inrev_activity_domain(self):
        active_ids = self._context.get('active_ids')
        exp_lines = self.env['hr.expense.line'].browse(active_ids)
        inrev_activities = exp_lines.mapped('activity_id.inrev_activity_ids')
        return [('id', 'in', inrev_activities.ids)]

    @api.multi
    def update_inrev_activity(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        exp_lines = self.env['hr.expense.line'].browse(active_ids)
        non_drafts = \
            exp_lines.filtered(lambda l: l.expense_state != 'draft').ids
        if non_drafts:
            raise ValidationError(
                _('Only draft internal charge can be set!'))
        exp_lines.write({'inrev_activity_id': self.inrev_activity_id.id})
