# -*- coding: utf-8 -*-
from openerp import models, fields


class ResProjectRevenueActual(models.Model):
    _name = 'res.project.revenue.actual'
    _description = 'Res Project Revenue Actual'

    m1 = fields.Float(
        'M1'
    )
    m2 = fields.Float(
        'M2'
    )
    m3 = fields.Float(
        'M3'
    )
    m4 = fields.Float(
        'M4'
    )
    m5 = fields.Float(
        'M5'
    )
    m6 = fields.Float(
        'M6'
    )
    m7 = fields.Float(
        'M7'
    )
    m8 = fields.Float(
        'M8'
    )
    m9 = fields.Float(
        'M9'
    )
    m10 = fields.Float(
        'M10'
    )
    m11 = fields.Float(
        'M11'
    )
    m12 = fields.Float(
        'M12'
    )
    project_id = fields.Many2one(
        'res.project',
        'Project'
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        'Fiscal Year'
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        'Activity Group'
    )
    income_section_id = fields.Many2one(
        'res.section',
        'Income Section'
    )
    sync_budget_line_id = fields.Integer(
        'Sync Budget Line'
    )
    budget_id = fields.Integer(
        'Budget'
    )
    charge_type = fields.Char(
        'Charge Type',
        size=255
    )
    budget_method = fields.Char(
        'Budget Method',
        size=255
    )
    description = fields.Text(
        'Description'
    )
    actual_amount = fields.Float(
        'Actual Amount'
    )
    released_amount = fields.Float(
        'Released Amount'
    )
    synced = fields.Boolean(
        'Synced'
    )
    last_sync = fields.Datetime(
        'Last Sync'
    )
    
