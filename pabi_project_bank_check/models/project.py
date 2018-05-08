# -*- coding: utf-8 -*-
from openerp import models, fields


class ResProject(models.Model):
    _inherit = 'res.project'

    journal_ids = fields.Many2many(
        'account.journal',
        'project_journal_rel',
        'journal_id', 'project_id',
        string='Project specific bank accounts',
        help="These bank account can be used on this project."
    )
