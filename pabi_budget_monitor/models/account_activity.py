# -*- coding: utf-8 -*-
from openerp import fields, models


# class AccountActivityGroup(models.Model):
#     _inherit = 'account.activity.group'
#
#     monitor_unit_ids = fields.One2many(
#         'account.activity.group.monitor.unit.view',
#         'activity_group_id',
#         string='Activity Group Monitor',
#         help="Plan vs actual per fiscal year for activity group"
#     )
#
#
# class AccountActivity(models.Model):
#     _inherit = 'account.activity'
#
#     monitor_unit_ids = fields.One2many(
#         'account.activity.monitor.unit.view',
#         'activity_id',
#         string='Activity Monitor',
#         help="Plan vs actual per fiscal year for activity"
#     )
