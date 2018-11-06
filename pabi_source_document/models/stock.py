# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        # From Sale
        if picking.sale_id:
            vals.update({
                'source_document_id': '%s,%s' % ('sale.order',
                                                 picking.sale_id.id),
                'source_document': picking.sale_id.name,
            })
        else:
            # From Purchase
            for move in picking.move_lines:  # stop when found
                purchase = move.purchase_line_id.order_id
                if purchase:
                    vals.update({
                        'source_document_id': '%s,%s' % ('purchase.order',
                                                         purchase.id),
                        'source_document': purchase.name,
                    })
                    break
        return super(StockPicking, self)._create_invoice_from_picking(picking,
                                                                      vals)

    def copy(self, cr, uid, id, default=None, context=None):
        """ kittiu: don't know why it is passing value this way too """
        if default is None:
            default = {}
        picking = self.browse(cr, uid, id)
        if picking.group_id:
            raise ValidationError(
                _('Duplication of document (with source) not allowed!'))
        return super(StockPicking, self).copy(cr, uid, id, default=default,
                                              context=context)
