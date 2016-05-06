# -*- coding: utf-8 -*-
from openerp import api, fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    @api.model
    def _ou_domain(self):
        return [('id', 'in', [g.id for g in self.env.user.operating_unit_ids])]
