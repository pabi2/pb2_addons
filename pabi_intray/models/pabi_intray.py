# -*- coding: utf-8 -*-
from openerp import models, fields


class PABIIntray(models.Model):
    """ Extension Data for Intray Messsage """
    _name = 'pabi.intray'
    _descripion = 'PABI Intray Extension'

    message_id = fields.Many2one(
        'mail.message',
        string='Message ID',
        readonly=True,
    )
    owner = fields.Char(
        string='Owner Emp ID',
        readonly=True,
        size=100,
    )
    boss = fields.Char(
        string='Boss Emp ID',
        readonly=True,
        size=100,
    )
    action = fields.Selection(
        [('A', 'Approve'),
         ('R', 'Reject')],
        string='Action Type',
        readonly=True,
    )
    is_complete = fields.Boolean(
        string='Complete Flow?',
        readonly=True,
        default=False,
    )
    url = fields.Char(
        string='URL',
        readonly=True,
        size=500,
        help="URL without <server>, will be joining with web.base.url",
    )
