# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockRequest(models.Model):
    _inherit = 'stock.request'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="['|',"
        "('project_ids', 'in', [project_id or -1]),"
        "('section_ids', 'in', [section_id or -1]),"
        "]",
    )

    @api.model
    def _get_default_fund(self):
        # If that dimension have 1 funds, use that fund.
        # If that dimension have no funds, use NSTDA
        # Else return false
        fund_id = False
        funds = False
        if self.project_id:
            funds = self.project_id.fund_ids
        if self.section_id:
            funds = self.section_id.fund_ids
        # Get default fund
        if len(funds) == 1:
            fund_id = funds[0].id
        else:
            fund_id = False
        return fund_id

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.section_id = self.employee_id.section_id

    # Section
    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            if 'project_id' in self:
                self.project_id = False
            self.fund_id = self._get_default_fund()

    # Project Base
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            if 'section_id' in self:
                self.section_id = False
            self.fund_id = self._get_default_fund()

    @api.model
    def _prepare_picking_line(self, line, picking,
                              location_id,
                              location_dest_id):
        data = super(StockRequest, self).\
            _prepare_picking_line(line, picking, location_id, location_dest_id)
        data.update({'project_id': line.request_id.project_id.id,
                     'section_id': line.request_id.section_id.id,
                     'fund_id': line.request_id.fund_id.id,
                     })
        return data


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
