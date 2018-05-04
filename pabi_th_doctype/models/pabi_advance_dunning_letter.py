# -*- coding: utf-8 -*-
from openerp import models, api, fields


class PABIAdvanceDunningLetter(models.Model):
    _inherit = 'pabi.advance.dunning.letter'

    name = fields.Char(
        default=False,  # Overwrite, make sure no number is created
    )

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'advance_dunning_letter'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        fiscalyear_id = self.env['account.fiscalyear'].find()
        # --
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        # It will try to use doctype_id first, if not available, rollback
        name = self.env['ir.sequence'].get('advance.dunning')
        vals.update({'name': name})
        return super(PABIAdvanceDunningLetter, self).create(vals)
