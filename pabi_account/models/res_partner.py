# -*- coding: utf-8 -*-
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bank_ids = fields.One2many(
        domain=['|', ('active', '=', False), ('active', '=', True)]
    )
    bank_account_history_ids = fields.One2many(
        'res.partner.bank.change.history',
        'partner_id',
        string='Change History',
        copy=False,
    )


class ResPartnerBankChangeHistory(models.Model):
    _name = 'res.partner.bank.change.history'
    _description = 'Change History, create / update / delete'
    _order = 'write_date desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
        index=True,
        ondelete='cascade',
    )
    bank_account = fields.Char(
        string='Bank Account',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Modifier',
        readonly=True,
    )
    write_date = fields.Datetime(
        string='Write Date',
        readonly=True,
    )
    action = fields.Selection(
        [('create', 'Create'),
         ('update', 'Update'),
         ('delete', 'Delete'),
         ('approve', 'Approve'),
         ('unapprove', 'Unapprove')],
        string='Action',
        readonly=True,
    )
    note = fields.Text(
        string='Note',
        readonly=False,
    )
