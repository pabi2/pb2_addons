# -*- coding: utf-8 -*-
from openerp import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    origin_id = fields.Many2one(
        'purchase.order',
        string='Original Purchase Order',
    )
    parent_id = fields.Many2one(
        'purchase.order',
        string='Original Purchase Order',
    )
    revision_no = fields.Integer(
        string='Revision No.',
    )

    @api.multi
    def action_make_revision(self):
        self.ensure_one()
        new_po_rev_no = 0
        if not self.revision_no:
            new_po_rev_no = 1
        else:
            new_po_rev_no += 1
        if not self.origin_id:
            new_origin_id = self.id
        else:
            new_origin_id = self.origin_id.id
        vals = {
            'name': self.name + '-' + str(new_po_rev_no),
            'revision_no': new_po_rev_no,
            'parent_id': self.id,
            'origin_id': new_origin_id,
        }
        new_po = self.copy(vals)
        action = {}
        Data = self.env['ir.model.data']
        res = Data.get_object_reference('purchase', 'view_purchase_order_form')
        action['views'] = [(res and res[1] or False, 'form')]
        action['res_id'] = new_po.id or False
        return action
