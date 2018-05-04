# -*- coding: utf-8 -*-
from openerp import fields, models, api


class WkfCmdBossLevelApproval(models.Model):
    _name = 'wkf.cmd.boss.level.approval'
    _description = 'Boss Level Approval'

    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        related='section_id.division_id',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        related='section_id.division_id',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
        related='section_id.sector_id',
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

    @api.model
    def get_supervisor(self, employee_id):
        """ Given employee, find subordinate """
        if not employee_id:
            return False
        employee = self.env['hr.employee'].browse(employee_id)
        levels = self.search([('section_id', '=', employee.section_id.id)])
        levels = levels.sorted(key=lambda l: l.level.sequence, reverse=False)
        supervisor_id = False
        employee_level = False
        if not levels:
            return False
        else:
            if employee not in levels.mapped('employee_id'):
                supervisor_id = levels[0].employee_id.id
            else:
                is_next_level = False
                for level in levels:
                    if is_next_level:
                        if employee_level == level.level:
                            continue
                        supervisor_id = level.employee_id.id
                        break
                    if level.employee_id == employee:
                        employee_level = level.level
                        is_next_level = True
                # Top most level, next level is not yet set to True,
                if not is_next_level:
                    supervisor_id = employee.id
        return supervisor_id


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
