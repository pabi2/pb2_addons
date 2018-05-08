# -*- coding: utf-8 -*-
from openerp import fields, api


class ResCommon(object):

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    name_short = fields.Char(
        string='Short Name',
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
    ehr_id = fields.Char(
        string='EHR-ID',
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

    # Domain name_search
    # This is a required variable, if any object with ResCommon needs to domain
    # They need to have context in view
    _rescommon_name_search_list = []

    @api.model
    def _add_name_search_domain(self):
        """ Additiona domain for context's name serach """
        domain = []
        ctx = self._context.copy()
        for i in self._rescommon_name_search_list:
            if ctx.get(i):
                domain += [(i, '=', ctx.get(i))]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if args is None:
            args = []
        args += self._add_name_search_domain()
        return super(ResCommon, self).name_search(name=name, args=args,
                                                  operator=operator,
                                                  limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0,
                    limit=None, order=None):
        if domain is None:
            domain = []
        domain += self._add_name_search_domain()
        res = super(ResCommon, self).search_read(domain=domain, fields=fields,
                                                 offset=offset, limit=limit,
                                                 order=order)
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        if domain is None:
            domain = []
        domain += self._add_name_search_domain()
        res = super(ResCommon, self).read_group(domain, fields, groupby,
                                                offset=offset, limit=limit,
                                                orderby=orderby, lazy=lazy)
        return res
