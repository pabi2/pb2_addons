# -*- coding: utf-8 -*-
from openerp import fields, api, _


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
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    special = fields.Boolean(
        string='Non-Standard',
        default=False,
        help="Specially used, i.e., Special Project GL",
    )
    display_name_2 = fields.Char(
        'Diaplsy Name 2 as [code] name',
        compute='_compute_display_name_2',
    )

    @api.multi
    def _compute_display_name_2(self):
        for rec in self:
            rec.display_name_2 = '[%s] %s' % (rec.code, rec.name)

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

    @api.one
    def copy_data(self, default=None):
        if default is None:
            default = {}
        tmp_default = dict(default, name=_("%s (Copy)") % self.name)
        return super(ResCommon, self).copy_data(default=tmp_default)
