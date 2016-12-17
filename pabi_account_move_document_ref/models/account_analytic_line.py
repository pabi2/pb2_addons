# -*- coding: utf-8 -*-
from openerp import models, fields
from .account_move import REFERENCE_SELECT, DOCTYPE_SELECT


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    document = fields.Char(
        string='Document',
        related='move_id.document',
        store=True,
        readonly=True,
    )
    document_id = fields.Reference(
        REFERENCE_SELECT,
        string='Document',
        related='move_id.document_id',
        store=True,
        readonly=True,
    )
    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        related='move_id.doctype',
        store=True,
        help="Use selection as refer_type in res_doctype",
    )
