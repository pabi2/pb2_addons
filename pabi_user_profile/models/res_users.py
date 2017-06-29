# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

#     employee_ids = fields.One2many(
#         'hr.employee',
#         'user_id',
#         string='Related employees'
#     )
    default_operating_unit_id = fields.Many2one(
        compute='_compute_operating_unit',
        store=True,
        required=False,
    )
    operating_unit_ids = fields.Many2many(
        compute='_compute_operating_unit',
        store=True,
        required=False,
    )

    @api.one
    @api.depends('employee_ids.org_id', 'employee_ids.org_ids')
    def _compute_operating_unit(self):
        org = self.employee_ids and self.employee_ids[0].org_id or False
        orgs = self.employee_ids and self.employee_ids[0].org_ids or False
        self.default_operating_unit_id = org and org.operating_unit_id
        self.operating_unit_ids = False
        if org and org.operating_unit_id:
            self.operating_unit_ids |= org.operating_unit_id
        if orgs and orgs.mapped('operating_unit_id'):
            self.operating_unit_ids |= orgs.mapped('operating_unit_id')
