# -*- coding: utf-8 -*-

from openerp import models
from openerp.osv.expression import get_unaccent_wrapper


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):

            self.check_access_rights(cr, uid, 'read')
            where_query = self._where_calc(cr, uid, args, context=context)
            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
            from_clause, where_clause, where_clause_params =\
                where_query.get_sql()
            where_str =\
                where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(cr)

            query = """SELECT id
                         FROM res_partner
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent})
                     -- ORDER BY {display_name}
                    """.format(where=where_str, operator=operator,
                               email=unaccent('email'),
                               display_name=unaccent('display_name'),
                               percent=unaccent('%s'))

            where_clause_params += [search_name, search_name]
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            cr.execute(query, where_clause_params)
            ids = map(lambda x: x[0], cr.fetchall())
            # patch for record from translation
            translation_obj = self.pool.get('ir.translation')
            trans_name = '%s,%s' % (self._model, 'name')
            translation_ids =\
                translation_obj.search(cr, uid, [('value', 'ilike', name),
                                                 ('name', '=', trans_name)],
                                       limit=limit, context=context)
            translations = translation_obj.browse(cr, uid,
                                                  translation_ids,
                                                  context=context)
            record_ids = [t.res_id for t in translations]
            ids = list(set(ids) | set(record_ids))
            # patch over
            if ids:
                return self.name_get(cr, uid, ids, context)
            else:
                return []
        return super(ResPartner, self).name_search(cr, uid, name, args,
                                                   operator=operator,
                                                   context=context,
                                                   limit=limit)
