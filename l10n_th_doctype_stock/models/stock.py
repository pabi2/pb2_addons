# -*- coding: utf-8 -*-
from openerp import models, api


_DOCTYPE = {'incoming': 'incoming_shipment',
            'outgoing': 'delivery_order',
            'internal': 'internal_transfer'}


class StockPickng(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        # Find doctype_id
        picking_type_id = vals.get('picking_type_id', False)
        code = self.env['stock.picking.type'].browse(picking_type_id).code
        refer_type = _DOCTYPE.get(code)
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        return super(StockPickng, self).create(vals)
