# -*- coding: utf-8 -*-
from openerp import fields, models


class ResProject(models.Model):
    _inherit = 'res.project'

    member_ids = fields.One2many(
        'res.project.member',
        'project_id',
        string='Project Member',
        copy=False,
    )


class ResProjectMember(models.Model):
    _name = 'res.project.member'
    _description = 'Project Member'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    project_position = fields.Selection([
        ('manager', "Project Manager"),
        ('member', "Member"), ],
        string='Position',
        required=True,
    )
