# -*- coding: utf-8 -*-
from openerp import fields, api
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon


class ActivityCommon(ActivityCommon):

    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity Rpt',
    )

    @api.multi
    def write(self, vals):
        if vals.get('activity_id', False):  # activity_rpt_id always follow
            vals.update({'activity_rpt_id': vals.get('activity_id')})
        return super(ActivityCommon, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('activity_id', False):  # activity_rpt_id always follow
            vals.update({'activity_rpt_id': vals.get('activity_id')})
        return super(ActivityCommon, self).create(vals)

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            self.activity_rpt_id = self.activity_id
        return super(ActivityCommon, self)._onchange_activity_id()

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        self.activity_rpt_id = False
        return super(ActivityCommon, self)._onchange_activity_group_id()
