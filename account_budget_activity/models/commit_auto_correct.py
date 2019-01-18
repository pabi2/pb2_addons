# -*- coding: utf-8 -*-
import logging
from openerp import models, api


_logger = logging.getLogger(__name__)


class CommitAutoCorrect(models.Model):
    _inherit = 'budget.transition'

    @api.model
    def commit_auto_correct(self, limit=50):
        """
        This job will help in correcting some of
        the non sense budget commitment
        For any active document with net amount > 0.0
        1. recreate_all_budget_commitment
        2. if not corrrected, release_all_committed_budget (ensure no positive)
        """
        models = ['purchase.request', 'purchase.order', 'hr.expense.expense']
        # 1) Recreate Budget Commitment
        for m in models:
            objs = self.env[m].search([('net_committed_amount', '>', 0.01)],
                                      limit=limit)
            for obj in objs:
                obj.recreate_all_budget_commitment()
                _logger.info(u'RECREATE COMMIT - %s', obj.display_name)
        # 2) Release All Budget Commitment
        for m in models:
            objs = self.env[m].search([('net_committed_amount', '>', 0.01)],
                                      limit=limit)
            for obj in objs:
                obj.release_all_committed_budget()
                _logger.info(u'RELEASE COMMIT - %s', obj.display_name)
        return True
