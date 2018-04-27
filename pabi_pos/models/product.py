# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="[('activity_group_ids', 'in', [activity_group_id])]",
    )

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        self.activity_id = False
