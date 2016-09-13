# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockRequest(models.Model):
    _inherit = 'stock.request'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        domain="['|',"
        "('project_ids', 'in', [project_id or 0]),"
        "('section_ids', 'in', [section_id or 0]),"
        "]",
    )


class ResProject(models.Model):
    _inherit = 'res.project'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Find matched project manager's projects
        project_manager_emp_id = self._context.get('project_manager_emp_id',
                                                   False)
        if project_manager_emp_id:
            PM = self.env['res.project.member']
            projects = PM.search([('project_position', '=', 'manager'),
                                  ('employee_id', '=', project_manager_emp_id)
                                  ])
            args += [('id', 'in', projects._ids)]
        return super(ResProject, self).name_search(name=name,
                                                   args=args,
                                                   operator=operator,
                                                   limit=limit)


class ResSection(models.Model):
    _inherit = 'res.section'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Find all section under the division of this requester
        employee_id = self._context.get('employee_id', False)
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            division_id = employee.section_id.division_id.id
            args += [('division_id', '=', division_id)]
        return super(ResSection, self).name_search(name=name,
                                                   args=args,
                                                   operator=operator,
                                                   limit=limit)
