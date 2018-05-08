# -*- coding: utf-8 -*-
from openerp import models, fields, api

OVERDUE_DAYS = {'l1': 7, 'l2': 14, 'l3': 19}


class CreateDunningLetter(models.TransientModel):
    _name = 'create.dunning.letter'

    @api.multi
    def action_create_dunning_letter(self):
        active_ids = self._context.get('active_ids', [])
        model = self._context.get('active_model')
        # - overdue > 7 days (14, 19)
        # - letter 1 is not created (2, 3)
        # - No letters created today
        today = fields.Date.context_today(self)
        for t in ['l1', 'l2', 'l3']:
            dunnings = self.env[model].browse(active_ids)
            filtered_dunning = dunnings.filtered(
                lambda l: l.days_overdue >= OVERDUE_DAYS[t] and not l[t] and
                today not in (l.l1_date, l.l2_date, l.l3_date)
            )
            filtered_dunning._create_dunning_letter(t)
            active_ids = list(set(active_ids) - set(filtered_dunning.ids))
        return True
