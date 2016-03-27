# -*- coding: utf-8 -*-
from openerp import fields, models

BUDGETING_LEVEL = {
   'activity_group_id': 'Activity Group',
   # 'activity_id': 'Activity',  # No activity level
   # Project Based
   'spa_id': 'SPA',
   'mission_id': 'Mission',
   'program_scheme_id': 'Program Scheme',
   'program_group_id': 'Program Group',
   'program_id': 'Program',
   'project_group_id': 'Project Group',
   'project_id': 'Project',
}

BUDGETING_LEVEL_UNIT = {
   'activity_group_id': 'Activity Group',
   # 'activity_id': 'Activity',  # No activity level
   # Unit Based
   'org_id': 'Org',
   'sector_id': 'Sector',
   'department_id': 'Department',
   'division_id': 'Division',
   'section_id': 'Section',
   'costcenter_id': 'Costcenter',
}


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    # Overwrite budgeting_level
    budgeting_level = fields.Selection(
        BUDGETING_LEVEL.items(),
        string='Project Based - Budgeting Level',
        required=True,
        default='program_id',
    )
    budgeting_level_unit = fields.Selection(
        BUDGETING_LEVEL_UNIT.items(),
        string='Unit Based - Budgeting Level',
        required=True,
        default='activity_group_id',
    )
