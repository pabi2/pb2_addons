# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError, ValidationError


class AccountActivityGroup(models.Model):
    _name = 'account.activity.group'
    _description = 'Activity Group'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    name = fields.Char(
        string='Activity Group',
        required=True,
    )
    description = fields.Char(
        string='Description',
    )
    parent_id = fields.Many2one(
        'account.activity.group',
        string='Parent Activity Group',
        index=True,
        ondelete='cascade',
    )
    child_id = fields.One2many(
        'account.activity.group',
        'parent_id',
        string='Child Activity Group',
    )
    parent_left = fields.Integer(
        string='Left Parent',
        select=True,
    )
    parent_right = fields.Integer(
        string='Right Parent',
        select=True,
    )
    activity_ids = fields.Many2many(
        'account.activity',
        'activity_group_activity_rel',
        'activity_group_id', 'activity_id',
        string='Activities',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    monitor_ids = fields.One2many(
        'account.activity.group.monitor.view',
        'activity_group_id',
        string='Activity Group Monitor',
        help="Plan vs actual per fiscal year for activity group"
    )
    _sql_constraints = [
        ('activity_uniq', 'unique(name)',
         'Activity Group must be unique!'),
        ('account_uniq', 'unique(account_id)',
         'Each Activity Group must have unique account'),
    ]

    @api.multi
    @api.constrains('parent_id')
    def _check_recursion(self):
        if self.parent_id and \
                not super(AccountActivityGroup, self)._check_recursion():
            raise UserError(
                _('You cannot create recursive Activity Group!'))

#     @api.one
#     @api.constrains('account_id', 'activity_ids')
#     def _check_account_id(self):
#         if not self.account_id and \
#                 self.env['account.activity'].search_count(
#                     [('activity_group_id', '=', self.id),
#                      ('account_id', '=', False)]) > 0:
#             raise UserError(
#                 _('Please select account in group or in activity!'))


class AccountActivity(models.Model):
    _name = 'account.activity'
    _description = 'Activity'

    activity_group_ids = fields.Many2many(
        'account.activity.group',
        'activity_group_activity_rel',
        'activity_id', 'activity_group_id',
        string='Activity Groups',
    )
    tag_ids = fields.Many2many(
        'account.activity.tag',
        'account_activity_tag_rel',
        'activity_id', 'tag_id',
        string='Tags',
        ondelete='restrict',
    )
    name = fields.Char(
        string='Activity',
        required=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
        domain=[('type', '!=', 'view')],
        help="This account has higher priority to group activities's account",
    )
    monitor_ids = fields.One2many(
        'account.activity.monitor.view',
        'activity_id',
        string='Activity Monitor',
        help="Plan vs actual per fiscal year for activity"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    search_keywords = fields.Text(
        string='Search Keywords',
    )
    _sql_constraints = [
        ('activity_uniq', 'unique(name, activity_group_id)',
         'Activity must be unique per group!'),
    ]

#     @api.multi
#     def name_get(self):
#         result = []
#         for activity in self:
#             result.append(
#                 (activity.id,
#                  "%s / %s" % (activity.activity_group_id.name or '-',
#                               activity.name or '-')))
#         return result

#     @api.one
#     @api.constrains('account_id')
#     def _check_account_id(self):
#         if not self.account_id and not self.activity_group_id.account_id:
#             raise UserError(
#                 _('Please select account for activity in group %s!' %
#                   (self.activity_group_id.name,)))


class AccountActivityTag(models.Model):
    _name = 'account.activity.tag'
    _description = 'Activity Tags'

    name = fields.Char(
        string='Name',
    )
    _sql_constraints = [
        ('activity_tag_uniq', 'unique(name)',
         'Activity Tag be unique!'),
    ]


class ActivityCommon(object):

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="[('activity_group_ids', 'in', [activity_group_id or 0])]",
    )

    @api.model
    def _onchange_focus_field(self, focus_field=False,
                              parent_field=False, child_field=False):
        """ Helper method
            - assign domain to child_field
            - assign value to parent field
        """
        if parent_field:
            if self[focus_field] and parent_field in self[focus_field]:
                if parent_field in self:
                    self[parent_field] = self[focus_field][parent_field]
        if child_field:
            child_domain = []
            if self[focus_field]:
                child_ids = self.env[self[child_field]._name].\
                    search([(focus_field, '=', self[focus_field].id)])
                if self[child_field] not in child_ids:
                    self[child_field] = False
                child_domain = [(focus_field, '=', self[focus_field].id)]
            else:
                self[child_field] = False
            return {'domain': {child_field: child_domain}}
        return {'domain': {}}

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if 'product_id' in self:
            self['product_id'] = False
        return self._onchange_focus_field(focus_field='activity_id',
                                          parent_field='account_id',
                                          child_field=False)

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        self.activity_id = False

    @api.multi
    @api.constrains('activity_id', 'product_id')
    def _check_activity_product_id(self):
        for rec in self:
            if 'product_id' in rec and 'activity_id' in rec:
                if rec.product_id and rec.activity_id:
                    raise ValidationError(
                        _("Activity/Product can not exist together!"))
