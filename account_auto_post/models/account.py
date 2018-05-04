# -*- coding: utf-8 -*-
import logging
from openerp import models, api

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def process_account_post(self, journal_ids=None, exclude_journal_ids=None):
        if not journal_ids and not exclude_journal_ids:
            filters = [('state', '=', 'draft')]
        else:
            filters = [('state', '=', 'draft')]
            if journal_ids:
                filters.append(('journal_id', 'in', journal_ids))
            if exclude_journal_ids:
                filters.append(('journal_id', 'not in', exclude_journal_ids))
        moves = self.search(filters, limit=1000)
        try:
            if moves:
                moves.button_validate()
        except Exception:
            _logger.exception("Failed processing account posting")
