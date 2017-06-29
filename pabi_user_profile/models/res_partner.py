# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee_code = fields.Char(
        related='employee_id.employee_code',
        string="Employee Code",
        store=True,
        readonly=True,
    )
