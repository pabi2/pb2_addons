# -*- coding: utf-8 -*-
from openerp import models, fields


class ResSection(models.Model):
    _inherit = 'res.section'
    
    employee_rpt_ids = fields.Many2many(
        'hr.employee',
        'hr_section_rpt_rel',
        'section_id',
        'employee_id',
        string='Report')
