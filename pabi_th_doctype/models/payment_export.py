# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PaymentExport(models.Model):
    _inherit = 'payment.export'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('name')
    def _compute_doctype(self):
        refer_type = 'payment_export'
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        document = super(PaymentExport, self).create(vals)
        if document.doctype_id.sequence_id:
            sequence_id = document.doctype_id.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            document.name = next_number
        return document
