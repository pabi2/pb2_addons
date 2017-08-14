# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # @api.one
    # @api.constrains('journal_id')
    # def _check_journal_id(self):
    #     if self.journal_id and len(self.search([('journal_id', '=',
    #                                         self.journal_id.id)])._ids) > 1:
    #         raise ValidationError(_("An Account Journal can't "
    #                                 "be used for more than 1 bank account"))
