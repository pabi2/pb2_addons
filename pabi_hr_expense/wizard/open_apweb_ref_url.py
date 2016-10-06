# -*- coding: utf-8 -*-
from openerp import models, api


class OpenAPWebRefURL(models.TransientModel):
    _name = "open.apweb.ref.url"

    @api.multi
    def open(self):
        self.ensure_one()
        print self._context
        url = self._context.get('apweb_ref_url')
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }
