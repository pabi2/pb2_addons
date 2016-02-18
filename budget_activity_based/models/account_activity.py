# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class AccountActivityGroup(models.Model):
    _name = 'account.activity.group'
    _description = 'Activity Group'

    name = fields.Char(
        string='Activity Group',
        required=True,
    )
    activity_ids = fields.One2many(
        'account.activity',
        'activity_group_id',
        string='Activities',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain=[('type', '!=', 'view')],
        help="This account has less priority to activitie's account",
    )
    _sql_constraints = [
        ('activity_uniq', 'unique(name)',
         'Activity Group must be unique!'),
    ]

    @api.one
    @api.constrains('account_id', 'activity_ids')
    def _check_account_id(self):
        if not self.account_id and \
                self.env['account.activity'].search_count(
                    [('activity_group_id', '=', self.id),
                     ('account_id', '=', False)]) > 0:
            raise UserError(
                _('Please select account in group or in activity!'))


class AccountActivity(models.Model):
    _name = 'account.activity'
    _description = 'Activity'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    name = fields.Char(
        string='Activity',
        required=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        domain=[('type', '!=', 'view')],
        help="This account has higher priority to group activities's account",
    )
    _sql_constraints = [
        ('activity_uniq', 'unique(name, activity_group_id)',
         'Activity must be unique per group!'),
    ]

    @api.multi
    def name_get(self):
        result = []
        for activity in self:
            result.append(
                (activity.id,
                 "%s / %s" % (activity.activity_group_id.name or '-',
                              activity.name or '-')))
        return result

    @api.one
    @api.constrains('account_id')
    def _check_account_id(self):
        if not self.account_id and not self.activity_group_id.account_id:
            raise UserError(
                _('Please select account for activity in group %s!' %
                  (self.activity_group_id.name,)))
