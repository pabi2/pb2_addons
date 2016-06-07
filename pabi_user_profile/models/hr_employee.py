# -*- coding: utf-8 -*-
from openerp import fields, models


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    title_id = fields.Many2one(
        'res.partner.title',
        string='Title',
        required=True,
    )
    first_name = fields.Char(
        string='First Name',
        required=True,
    )
    mid_name = fields.Char(
        string='Middle Name',
    )
    last_name = fields.Char(
        string='Last Name',
        required=True,
    )
    employee_code = fields.Char(
        string='Employee ID.',
        required=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    org_id = fields.Many2one(
        'res.org',
        related='section_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )
    org_ids = fields.Many2many(
        'res.org',
        'org_employee_rel',
        'employee_id', 'org_id',
        string='Additional Orgs',
        help="More Orgs that this employee have access to",
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        related='section_id.costcenter_id',
        string='Cost Center',
        store=True,
    )
    position_id = fields.Many2one(
        'hr.position',
        string='Position',
        required=True,
    )
    position_management_id = fields.Many2one(
        'hr.position',
        string='Management Position',
    )
    is_management = fields.Boolean(
        string='Is Management',
    )
    # Kitti U. Remove this otherwise, can't update Related user on Employee
    # @Poon, will you have any other problem?
#     user_id = fields.Many2one(
#         'res.users',
#         related='resource_id.user_id',
#         string='User',
#         store=True,
#     )
