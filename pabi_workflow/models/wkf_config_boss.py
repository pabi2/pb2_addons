# -*- coding: utf-8 -*-
from openerp import fields, models


class WkfCmdBossLevelApproval(models.Model):
    _name = 'wkf.cmd.boss.level.approval'
    _description = 'Boss Level Approval'

    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='section_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    level = fields.Many2one(
        'wkf.cmd.level',
        string='Level',
        required=True,
    )
    create_date = fields.Datetime(
        string='Import Date',
        readonly=True,
    )


class WkfCmdBossSpecailLevel(models.Model):
    _name = 'wkf.cmd.boss.special.level'
    _description = 'Boss Special Level Approval'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    special_level = fields.Many2one(
        'wkf.cmd.level',
        string='Level',
        required=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )


class WkfCmdSectionAssign(models.Model):
    _name = 'wkf.cmd.section.assign'
    _description = 'Section Assignment'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )
