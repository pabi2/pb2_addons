# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class AccountMove(DoclineCommon, models.Model):
    _inherit = 'account.move'

    @api.multi
    @api.constrains('line_id')
    def _check_docline_seq(self):
        for move in self:
            self._compute_docline_seq('account_move_line',
                                      'move_id', move.id)
        return True


class AccountMoveLine(DoclineCommonSeq, models.Model):
    _inherit = 'account.move.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('account.move').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,
                                       'account_move',
                                       'account_move_line',
                                       'move_id')
