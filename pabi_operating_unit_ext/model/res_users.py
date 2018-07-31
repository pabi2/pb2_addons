# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        compute='_compute_access_all_operating_unit',
        store=True,
        default=False,
        help="This user belong to a group that can access of Operating Units",
    )

    @api.multi
    @api.depends('default_operating_unit_id.access_all_operating_unit',
                 'operating_unit_ids.access_all_operating_unit',
                 'groups_id.access_all_operating_unit')
    def _compute_access_all_operating_unit(self):
        OU = self.env['operating.unit']
        GRP = self.env['res.groups']
        for user in self:
            # If user's default OU and user's OUs, and user's Groups
            ou_ids = user.operating_unit_ids.ids or []
            ou_ids.append(user.default_operating_unit_id.id or 0)
            grp_ids = user.groups_id.ids
            all_ou = OU.search_count([
                ('id', 'in', ou_ids),
                ('access_all_operating_unit', '=', True)])
            all_ou += GRP.search_count([
                ('id', 'in', grp_ids),
                ('access_all_operating_unit', '=', True)])
            if all_ou > 0:
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
