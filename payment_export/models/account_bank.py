# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    lot_control_ids = fields.One2many(
        'cheque.lot.control',
        'bank_id',
        string='Cheque Lot Controls',
        copy=False,
    )

    @api.one
    @api.constrains('journal_id')
    def _check_journal_id(self):
        if self.journal_id and self.search_count([('journal_id', '=',
                                                   self.journal_id.id)]) > 1:
            raise ValidationError(_("An Account Journal can't "
                                    "be used for more than 1 bank"))
