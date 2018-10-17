# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseContract(models.Model):
    _inherit = 'purchase.contract'

    poc_code = fields.Char(
        readonly=False,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Last Updated By',
        readonly=False,
    )

    @api.multi
    def mork_set_write_uid_by_create_uid(self):
        for rec in self:
            rec.write_uid = rec.create_emp_id.user_id
        return True
