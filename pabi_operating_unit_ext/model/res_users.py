# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        compute='_compuate_access_all_operating_unit',
        store=True,
        default=False,
        help="This user belong to a group that can access of Operating Units",
    )

    @api.multi
    @api.depends('default_operating_unit_id.access_all_operating_unit',
                 'operating_unit_ids.access_all_operating_unit',
                 'groups_id.access_all_operating_unit')
    def _compuate_access_all_operating_unit(self):
        for user in self:
            if (user.default_operating_unit_id.access_all_operating_unit or
                    user.operating_unit_ids.
                    filtered('access_all_operating_unit') or
                    user.groups_id.filtered('access_all_operating_unit')):
                user.access_all_operating_unit = True
            else:
                user.access_all_operating_unit = False


class ResGroups(models.Model):
    _inherit = 'res.groups'

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        copy=False,
        help="With this checkbox checked, users in this Group "
        "will have access to all Operating Units")

    @api.multi
    def write(self, vals):
        res = super(ResGroups, self).write(vals)
        if 'access_all_operating_unit' in vals:
            for group in self:
                group.users.write({})  # Write to clear cache
        return res
