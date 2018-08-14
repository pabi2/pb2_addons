# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools


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
    )
    boss = fields.Char(
        string='Boss Emp ID',
        readonly=True,
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
        help="URL without <server>, will be joining with web.base.url"
    )

    def init(self, cr):
        """ View pabi_intray_view, to be used from external system, no ORM """
        tools.drop_view_if_exists(cr, 'pabi_intray_view')
        cr.execute("""CREATE or REPLACE VIEW pabi_intray_view as (
            select pi.id, pi.owner, pi.boss, pi.action, pi.is_complete,
            (select value from ir_config_parameter
             where key = 'web.base.url') || '?' || url as url,
            mm.subject, mm.body, mm.write_date
            from pabi_intray pi
            join mail_message mm on mm.id = pi.message_id
        )""")
