# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class OpenAPWebRefURL(models.TransientModel):
    _name = "open.apweb.ref.url"

    @api.multi
    def open(self):
        self.ensure_one()
        url = self._context.get('apweb_ref_url')
        if not url:
            raise UserError(_('No reference document found!'))
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }
