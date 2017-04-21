# -*- coding: utf-8 -*-
from openerp import fields, models, _, exceptions, api


class AccessRight(models.TransientModel):
    _name = "access.right"

    access_right = fields.Many2one('access.access',
                                   string='Meta Group',
                                   type="Selection")

    @api.multi
    def apply_access(self):
        active_id = self._context.get('active_id')
        for g in self:
            if self._context and active_id and g.access_right:
                user_rec = self.env['res.users'].browse(active_id)
                user_rec.groups_id = [(6, 0, g.access_right.groups_id.ids)]
            else:
                raise exceptions.Warning(
                    _('Please create a Meta Group via '
                      'Settings --> Users --> Meta Groups.'))
