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
        if self.ids:
            self._cr.execute("""
                update purchase_contract set write_uid = create_uid
                where id in %s
            """, (tuple(self.ids), ))
        return True
