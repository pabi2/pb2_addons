# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

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

    @api.multi
    @api.depends('employee_ids.org_id', 'employee_ids.org_ids')
    def _compute_operating_unit(self):
        for rec in self:
            org = rec.employee_ids and rec.employee_ids[0].org_id or False
            orgs = rec.employee_ids and rec.employee_ids[0].org_ids or False
            rec.default_operating_unit_id = org and org.operating_unit_id
            rec.operating_unit_ids = False
            if org and org.operating_unit_id:
                rec.operating_unit_ids |= org.operating_unit_id
            if orgs and orgs.mapped('operating_unit_id'):
                rec.operating_unit_ids |= orgs.mapped('operating_unit_id')
