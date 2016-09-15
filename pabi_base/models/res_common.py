# -*- coding: utf-8 -*-
from openerp import fields, api, models


class ResCommon(object):

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    name_short = fields.Char(
        string='Short Name',
        size=10,
        translate=True,
    )
    code = fields.Char(
        string='Code',
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            name_short = ('name_short' in rec) and rec['name_short'] or False
            result.append((rec.id, "%s%s" %
                           (rec.code and '[' + rec.code + '] ' or '',
                            name_short or name or '')))
        return result
