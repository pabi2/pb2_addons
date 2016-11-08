# -*- coding: utf-8 -*-
from openerp import models, fields, api

_DOCTYPE = {'request': 'stock_request',
            'borrow': 'stock_borrow',
            'transfer': 'stock_transfer'}


class StockRequest(models.Model):
    _inherit = 'stock.request'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('type')
    def _compute_doctype(self):
        refer_type = _DOCTYPE[self.type]
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        picking = super(StockRequest, self).create(vals)
        if picking.doctype_id.sequence_id:
            sequence_id = picking.doctype_id.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            picking.name = next_number
        return picking
