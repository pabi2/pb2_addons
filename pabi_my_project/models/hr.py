# -*- coding: utf-8 -*-
from openerp import models, fields


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    project_ids = fields.Many2many(
        'res.project',
        'project_hr_employee_rel',
        'employee_id',
        'project_id',
        string='Projects',
    )
