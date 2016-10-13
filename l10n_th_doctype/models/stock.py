# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


_DOCTYPE = {'incoming': 'incoming_shipment',
            'outgoing': 'delivery_order',
            'internal': 'internal_transfer'}


class StockPickng(models.Model):
    _inherit = 'stock.picking'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('picking_type_id')
    def _compute_doctype(self):
        code = self.picking_type_id.code
        refer_type = _DOCTYPE[code]
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        picking = super(StockPickng, self).create(vals)
        if picking.doctype_id.sequence_id:
            sequence_id = picking.doctype_id.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            picking.name = next_number
        return picking
