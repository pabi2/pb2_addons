# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError


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

    @api.one
    @api.constrains('project_id', 'employee_id', 'project_position')
    def _check_unique_project_manager(self):
        self._cr.execute("""
            select coalesce(count(*))
            from res_project_member
            where project_position = 'manager'
            and project_id = %s
        """, (self.project_id.id,))
        count = self._cr.fetchone()[0]
        if count > 1:
            raise UserError(_('There are project with > 1 project manager'))
