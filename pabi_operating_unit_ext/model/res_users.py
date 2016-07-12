# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        compute='_compuate_access_all_operating_unit',
        store=True,
        help="This user belong to a group that can access of Operating Units")

    @api.multi
    @api.depends('groups_id.access_all_operating_unit')
    def _compuate_access_all_operating_unit(self):
        for user in self:
            if user.groups_id.filtered('access_all_operating_unit'):
                user.access_all_operating_unit = True


class ResGroups(models.Model):
    _inherit = 'res.groups'

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        copy=False,
        help="With this checkbox checked, users in this Operating Unit "
        "will have access to all other Operating Unit too")
