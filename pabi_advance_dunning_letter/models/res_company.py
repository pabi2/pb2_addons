# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    group_email = fields.Char(
        string='Group Email',
        default='acf-adv@nstda.or.th',
    )
    head_account_employee_id = fields.Many2one(
        'hr.employee',
        string='Head Accounting',
    )
