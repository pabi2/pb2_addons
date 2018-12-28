# -*- coding: utf-8 -*-
from openerp import fields, models


class WkfCmdSpecialAmountProjectApproval(models.Model):
    _name = 'wkf.cmd.special.amount.project.approval'
    _description = 'Special Amount Project Approval'

    doctype_id = fields.Many2one(
        'wkf.config.doctype',
        string='Document Type',
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    amount_min = fields.Float(
        string="Minimum"
    )
    amount_max = fields.Float(
        string="Maximum"
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        related='employee_id.org_id',
    )
