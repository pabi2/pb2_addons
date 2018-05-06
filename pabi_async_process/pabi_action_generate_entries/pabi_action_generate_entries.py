# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _


class PabiActionGenerateEntries(models.TransientModel):
    """ PABI Action for Generate Entries """
    _name = 'pabi.action.generate.entries'
    _inherit = 'pabi.action'

    # Criteria
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='For Period',
        domain=[('state', '=', 'draft')],
        required=True,
    )
    date = fields.Date(
        string='Generate Entries Before',
        required=True,
    )
    message = fields.Text(
        string='Message',
        readonly=True,
    )
    model_type_ids = fields.Many2many(
        'account.model.type',
        string='Model Types',
        required=True,
    )

    @api.onchange('calendar_period_id')
    def _onchange_calendar_period(self):
        self.date = False
        self.message = False
        if self.calendar_period_id:
            self.date = self.calendar_period_id.date_stop
            dt = datetime.strptime(self.date, '%Y-%m-%d').strftime('%d/%m/%Y')
            message = _('\n This will generate recurring entries '
                        'before or equal to "%s".\n'
                        ' And all journal date will be "%s".') % (dt, dt)
            self.message = message

    @api.model
    def action_generate(self, date, end_period_date, model_type_ids):
        """ Revised function to be called from pabi.action """
        SLine = self.env['account.subscription.line']
        lines = SLine.search([('date', '<', date),
                              ('move_id', '=', False)])
        ctx = {'end_period_date': end_period_date,
               'model_type_ids': model_type_ids}
        move_ids = lines.with_context(ctx).move_create()
        records = self.env['account.move'].browse(move_ids)
        return records

    @api.multi
    def pabi_action(self):
        self.ensure_one()
        # Prepare job information
        process_xml_id = 'pabi_async_process.generate_entries'
        job_desc = 'Generate Entries for %s by %s' % \
            (self.calendar_period_id.display_name, self.env.user.display_name)
        func_name = 'action_generate'
        # Prepare kwargs, the params for method action_generate
        model_type_ids = self.model_type_ids.ids
        end_period_date = self.date
        date1 = \
            datetime.strptime(self.date, "%Y-%m-%d") + relativedelta(days=1)
        date = date1.strftime('%Y-%m-%d')
        kwargs = {'date': date,
                  'end_period_date': end_period_date,
                  'model_type_ids': model_type_ids, }
        # Call the function
        res = super(PabiActionGenerateEntries, self).\
            pabi_action(process_xml_id, job_desc, func_name, **kwargs)
        return res
