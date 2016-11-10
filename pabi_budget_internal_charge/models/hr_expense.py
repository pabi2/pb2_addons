# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        selection_add=[('internal', 'Internal Charge')],
    )
    internal_section_id = fields.Many2one(
        'res.section',
        string='Internal Section',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        compute='_compute_activity_group_id',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain=[('budget_method', '=', 'revenue')],
    )

    @api.multi
    @api.depends('activity_id')
    def _compute_activity_group_id(self):
        for rec in self:
            rec.activity_group_id = rec.activity_id.activity_group_ids and \
                rec.activity_id.activity_group_ids[0] or False
