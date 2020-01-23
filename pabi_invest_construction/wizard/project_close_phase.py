# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ProjectClosePhaseWizard(models.TransientModel):
    _name = 'project.close.phase.wizard'

    date_close = fields.Date(
        string='Close Date',
        default=lambda self: self.get_date()
    )

    @api.multi
    def close_project(self):
        active_id = self.env.context.get('active_id')
        phase = self.env['res.invest.construction.phase'].browse(active_id)
        phase.date_close = self.date_close
        phase.action_close()
        return True

    @api.multi
    def get_date(self):
        active_id = self.env.context.get('active_id')
        phase = self.env['res.invest.construction.phase'].browse(active_id)
        return phase.date_close
