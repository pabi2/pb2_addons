# -*- coding: utf-8 -*-
from openerp import models, fields, api


class InterfaceAccountEntry(models.Model):
    _inherit = 'interface.account.entry'

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
        refer_type = 'interface_account'
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.multi
    def execute(self):
        result = super(InterfaceAccountEntry, self).execute()
        for interface in self:
            if interface.doctype_id.sequence_id:
                # Get doctype sequence for document number
                sequence_id = interface.doctype_id.sequence_id.id
                fiscalyear_id = interface.period_id.fiscalyear_id.id
                interface.number = self.\
                    with_context(fiscalyear_id=fiscalyear_id).\
                    env['ir.sequence'].next_by_id(sequence_id)
                # Use document number for journal entry
                # interface.move_id.ref = interface.number
        return result

    @api.multi
    def write(self, vals):
        res = super(InterfaceAccountEntry, self).write(vals)
        if vals.get('move_id', False):
            for interface in self:
                if not interface.type == 'reverse':
                    continue
                if interface.doctype_id.reversal_sequence_id:
                    sequence_id = interface.doctype_id.reversal_sequence_id.id
                    fy_id = interface.move_id.period_id.fiscalyear_id.id
                    interface.move_id.write({
                        'name': self.with_context(fiscalyear_id=fy_id).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
        return res
