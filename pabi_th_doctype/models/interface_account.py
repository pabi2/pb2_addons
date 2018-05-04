# -*- coding: utf-8 -*-
from openerp import models, api


class InterfaceAccountEntry(models.Model):
    _inherit = 'interface.account.entry'

    @api.multi
    def execute(self):

        for interface in self:
            # Find doctype
            refer_type = 'interface_account'
            doctype = self.env['res.doctype'].get_doctype(refer_type)
            # --
            interface = interface.with_context(doctype_id=doctype.id)
            super(InterfaceAccountEntry, interface).execute()
        return True

    @api.multi
    def write(self, vals):
        res = super(InterfaceAccountEntry, self).write(vals)
        if vals.get('move_id', False):
            for interface in self:
                if not interface.type == 'reverse':
                    continue
                # get doctype
                refer_type = 'interface_account'
                doctype = self.env['res.doctype'].get_doctype(refer_type)
                # --
                if doctype.reversal_sequence_id:
                    sequence_id = doctype.reversal_sequence_id.id
                    fy_id = interface.move_id.period_id.fiscalyear_id.id
                    interface.move_id.write({
                        'name': self.with_context({'fiscalyear_id': fy_id}).
                        env['ir.sequence'].next_by_id(sequence_id),
                        'cancel_entry': True,
                    })
                    interface.number = interface.move_id.name
        return res
