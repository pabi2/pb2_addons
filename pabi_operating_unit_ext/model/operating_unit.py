# -*- coding: utf-8 -*-
from openerp import api, models, fields


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        copy=False,
        help="With this checkbox checked, users in this Operating Unit "
        "will have access to all other Operating Unit too")
    user_ids = fields.Many2many(
        'res.users',
        'operating_unit_users_rel',
        'poid', 'user_id',
        string='Users',
    )

#     @api.model
#     def _ou_domain(self):
#         if self.env.user.access_all_operating_unit:
#             return []
#         else:
#             return [('id', 'in', self.env.user.operating_unit_ids._ids)]

    @api.multi
    def write(self, vals):
        res = super(OperatingUnit, self).write(vals)
        if 'access_all_operating_unit' in vals:
            for ou in self:
                ou.user_ids.write({})  # Write to clear cache
        return res
