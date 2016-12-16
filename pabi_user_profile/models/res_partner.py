# -*- coding: utf-8 -*-
from openerp import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee_code = fields.Char(
        related='employee_id.employee_code',
        string="Employee Code",
        store=True,
        readonly=True,
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(
                [('employee_code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search(
                [('search_key', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
