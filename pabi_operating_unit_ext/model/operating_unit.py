# -*- coding: utf-8 -*-
from openerp import api, models, fields


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        copy=False,
        help="With this checkbox checked, users in this Operating Unit "
        "will have access to all other Operating Unit too")

    @api.model
    def _ou_domain(self):
        if self.env.user.access_all_operating_unit:
            return []
        else:
            return [('id', 'in', self.env.user.operating_unit_ids._ids)]
