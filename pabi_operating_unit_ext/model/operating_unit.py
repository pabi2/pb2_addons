# -*- coding: utf-8 -*-
from openerp import api, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    @api.model
    def _ou_domain(self):
        return [('id', 'in', [g.id for g in self.env.user.operating_unit_ids])]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(OperatingUnit, self).name_search(
            name, args=args, operator=operator, limit=limit)
        domain_ids = self._ou_domain()[0][2]  # Ensure domain
        return filter(lambda x: x[0] in domain_ids, res)
