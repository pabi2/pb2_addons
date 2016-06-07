# -*- coding: utf-8 -*-
from openerp import fields, models


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    section_assign_ids = fields.Many2many(
        'res.section',
        'wkf_cmd_section_assign',
        'employee_id',
        'section_id',
        string='Section Assignment',
    )
