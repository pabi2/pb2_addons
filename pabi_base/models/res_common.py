# -*- coding: utf-8 -*-
from openerp import fields, api


class ResCommon(object):

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s%s" %
                           (rec.code and '[' + rec.code + '] ' or '',
                            rec.name or '')))
        return result
