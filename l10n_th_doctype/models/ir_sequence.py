# -*- coding: utf-8 -*-
from openerp import models, fields, api


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    special_type = fields.Selection(
        selection_add=[('doctype', 'Doctype Sequence')]
    )

    @api.model
    def next_by_doctype(self):
        # Check if doctype in context is valid
        doctype_id = self._context.get('doctype_id', False)
        if doctype_id:
            doctype = self.env['res.doctype'].browse(doctype_id)
            sequence_id = doctype.sequence_id.id
            if sequence_id:
                return super(IrSequence, self).next_by_id(sequence_id)
        return False

    @api.model
    def next_by_id(self, sequence_id):
        number = self.next_by_doctype()
        return number or super(IrSequence, self).next_by_id(sequence_id)

    @api.model
    def next_by_code(self, sequence_code):
        EXCEPTION = ('account.analytic.account', 'account.reconcile')
        if sequence_code in EXCEPTION:
            return super(IrSequence, self).next_by_code(sequence_code)
        number = self.next_by_doctype()
        return number or super(IrSequence, self).next_by_code(sequence_code)
