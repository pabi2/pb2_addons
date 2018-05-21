# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountActivityGroup(models.Model):
    _inherit = "account.activity.group"

    # has_expense_rule = fields.Boolean(
    #     string='Has Expense Rule',
    #     default=False,
    # )
    special_workflow_emotion = fields.Boolean(
        string='Special Workflow Emotion',
        default=False,
        help="If checked, all activities related to this workflow will be set "
        "Special Workflow = 'Emotion'.\nIf unchecked, all activites related "
        "to this workflow will be set Special Workflow = False",
    )
    wf_emotion_section_ids = fields.Many2many(
        'res.section',
        'wf_emotion_activity_group_section_rel',
        'activity_group_id', 'section_id',
        string='Usable by Sections',
        help="Only these sections can use activity group with emotion workflow"
    )
    no_display = fields.Boolean(
        string='Not for general use',
        default=False,
        help="If checked,do not show this item on some apps, "
        "not to confuse user.",
    )

    @api.multi
    def write(self, vals):
        if 'special_workflow_emotion' in vals:
            for activity_group in self:
                special_workflow = \
                    vals.get('special_workflow_emotion') and 'emotion' or False
                activity_group.activity_ids.write({
                    'special_workflow': special_workflow,
                })
        res = super(AccountActivityGroup, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        activity_group = super(AccountActivityGroup, self).create(vals)
        if 'special_workflow_emotion' in vals:
            special_workflow = \
                vals.get('special_workflow_emotion') and 'emotion' or False
            activity_group.activity_ids.write({
                'special_workflow': special_workflow,
            })
        return activity_group

    # Inherit for issues/1173
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if self._context.get('expense_id', False):
            expense_id = self._context['expense_id']
            expense = self.env['hr.expense.expense'].browse(expense_id)
            domain = [('id', 'in', expense.activity_group_ids.ids)]
            args += domain
        return super(AccountActivityGroup, self).name_search(name=name,
                                                             args=args,
                                                             operator=operator,
                                                             limit=limit)


class AccountActivity(models.Model):
    _inherit = "account.activity"

    # has_expense_rule = fields.Boolean(
    #     string='Has Expense Rule',
    #     default=False,
    # )
    special_workflow = fields.Selection(
        [('fringe', 'Fringe'),
         ('recreation', 'Recreation'),
         ('emotion', 'Emotion'),
         ],
        string='Special Workflow',
        help="With different type, PABI Web will be using different workflow"
    )
