# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def convert_acc_number_to_journal(self, acc_number=False):
        """ Given acc_number must be 10 digits, we need to ensure that """
        _logger.info('Input acc_number = %s' % acc_number)
        acc_number = acc_number or ''
        acc_number = acc_number.strip()
        acc_number = acc_number.replace('-', '')
        acc_number = acc_number.zfill(10)
        acct = self.search([('acc_number', '=', acc_number)])
        if not acct:
            raise ValidationError(_('Bank Account : %s not found!') %
                                  acc_number)
        journal = acct.journal_id.name or ''
        _logger.info('Output journal = %s' % journal)
        return journal
