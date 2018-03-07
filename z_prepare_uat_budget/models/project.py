# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class ResProject(models.Model):
    _inherit = 'res.project'

    @api.model
    def copy_project_program(self, suffix):
        """ Copy all project and put '-PH2' as suffix """
        if not suffix:
            suffix = '-PH2'

        # 1) Copy Program
        programs = self.env['res.program'].search([])
        for program in programs:
            program.copy({'code': program.code + suffix,
                          'name': program.name + suffix})
        # 2) Copy Project Group and set new Program
        project_groups = self.env['res.project.group'].search([])
        Program = self.env['res.program']
        for project_group in project_groups:
            pg_id = Program.name_search(
                project_group.program_id.code + suffix)[0][0]
            project_group.copy({'code': project_group.code + suffix,
                                'name': project_group.name + suffix,
                                'program_id': pg_id})

        # 3) Copy Project and set new Project Group
        projects = self.env['res.project'].search([])
        ProjectGroup = self.env['res.project.group']
        for project in projects:
            pg_id = ProjectGroup.\
                name_search(project.project_group_id.code + suffix)[0][0]
            project.copy({'code': project.code + suffix,
                          'name': project.name + suffix,
                          'project_group_id': pg_id, })
