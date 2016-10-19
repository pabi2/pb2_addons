# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseWorkAcceptance(models.Model):
    _inherit = 'purchase.work.acceptance'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('order_id')
    def _compute_doctype(self):
        refer_type = 'work_acceptance'
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        work = super(PurchaseWorkAcceptance, self).create(vals)
        if work.doctype_id.sequence_id:
            sequence_id = work.doctype_id.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            work.name = next_number
        return work
