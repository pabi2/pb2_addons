# -*- coding: utf-8 -*-
from openerp import api, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    @api.model
    def _ou_domain(self):
        if self.env.user.access_all_operating_unit:
            return []
        else:
            return [('id', 'in', self.env.user.operating_unit_ids._ids)]
