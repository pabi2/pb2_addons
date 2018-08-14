# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools


# Extended name search is only used on some operators
ALLOWED_OPS = set(['ilike', 'like', '='])


@tools.ormcache(skiparg=0)
def _get_rec_names(self):
    "List of fields to search into"
    self._cr.execute("SELECT id from ir_model where model = %s", (self._name,))
    model_id = self._cr.fetchone()
    model_id = model_id and model_id[0] or False
    model = self.env['ir.model'].browse(model_id)
    rec_name = [self._rec_name] or []
    other_names = model.name_search_ids.mapped('name')
    return rec_name + other_names


def _extend_name_results_translation(self, field_name, name,
                                     operator, results, limit):
    result_count = len(results)
    limit = limit or 100
    if result_count < limit:
        trans_name = '%s,%s' % (self._model, field_name)

        # -------------------------------------------------------------------
        # kittiu: Sepcial Case for res_users, which use name from res_partner
        special_case = trans_name in ['res.users,name', 'account.tax,name']
        if special_case:
            if trans_name == 'res.users,name':
                trans_name = 'res.partner,name'
        # -------------------------------------------------------------------
        res = []
        if operator in ('like', 'ilike'):
            self._cr.execute("""
                SELECT res_id FROM ir_translation WHERE
                (src """ + operator + """ %s OR value """ + operator + """ %s)
                AND name = %s LIMIT %s
            """, ('%' + name + '%', '%' + name + '%', trans_name, limit))
            res = self._cr.dictfetchall()
        elif operator == '=':
            self._cr.execute("""
                SELECT res_id FROM ir_translation WHERE
                (src = %s OR value = %s) AND name = %s LIMIT %s
            """, (name, name, trans_name, limit))
            res = self._cr.dictfetchall()
        record_ids = [t['res_id'] for t in res]

        # -------------------------------------------------------------------
        # kittiu: Special case
        if special_case:  # need to change from res.partner to res.users
            # Partner
            if trans_name == 'res.partner,name':
                partners = self.env['res.partner'].browse(record_ids)
                user_ids = []
                for partner in partners:
                    user_ids += partner.user_ids.ids
                record_ids = user_ids
            # Tax
            if trans_name == 'account.tax,name':
                tax_domain = []
                if self._context.get('type') in ('out_invoice', 'out_refund'):
                    tax_domain += [('type_tax_use', 'in', ['sale', 'all'])]
                elif self._context.get('type') in ('in_invoice', 'in_refund'):
                    tax_domain += [('type_tax_use', 'in', ['purchase', 'all'])]
                if self._context.get('journal_id', False):
                    journal = self.env['account.journal'].\
                        browse(self._context.get('journal_id'))
                    tax_domain += \
                        [('type_tax_use', 'in', [journal.type, 'all'])]
                if tax_domain:
                    tax_ids = self.env['account.tax'].search(tax_domain).ids
                    record_ids = list(set(tax_ids).intersection(record_ids))
        # -------------------------------------------------------------------

        record_ids = self.search([('id', 'in', record_ids)])
        results.extend(record_ids.name_get())
        results = list(set(results))
    return results


def _extend_search_results_translation(self, sub_domain):
    field_name = sub_domain[0]
    value = sub_domain[2]
    trans_name = '%s,%s' % (self._model, field_name)
    # kittiu: Sepcial Case for res_users, which use name from res_partner
    special_case = trans_name == 'res.users,name'
    if special_case:
        trans_name = 'res.partner,name'
    # --
    if isinstance(value, str) or isinstance(value, unicode):
        value = value.replace("'", "''")  # Escape for SQL
        self._cr.execute("""
            SELECT src
            FROM ir_translation
            WHERE value ilike %s AND
                name = %s
        """, (value, trans_name))
        res = self._cr.fetchone()
        source_value = res and res[0] or False
        if source_value:
            sub_domain[2] = source_value
    return sub_domain


class ModelExtended(models.Model):
    _inherit = 'ir.model'

    name_search_ids = fields.Many2many(
        'ir.model.fields',
        string='Name Search Fields')

    def _register_hook(self, cr, ids=None):

        def make_name_search():

            @api.model
            def name_search(self, name='', args=None,
                            operator='ilike', limit=100):
                # Perform standard name search
                res = name_search.origin(
                    self, name=name, args=args, operator=operator, limit=limit)
                enabled = self.env.context.get('name_search_extended', True)
                # Perform extended name search
                # Note: Empty name causes error on
                #       Customer->More->Portal Access Management
                if name and enabled and operator in ALLOWED_OPS:
                    # Support a list of fields to search on
                    all_names = _get_rec_names(self)
                    # Try translation word search each of the search fields
                    for rec_name in all_names:
                        res = _extend_name_results_translation(
                            self, rec_name, name, operator, res, limit)
                return res
            return name_search

        def make_search():
            @api.model
            def _search(self, args, offset=0, limit=None, order=None,
                        count=False, access_rights_uid=None):
                # Perform standard _search
                result = _search.origin(
                    self, args=args, offset=offset, limit=limit, order=order,
                    count=count, access_rights_uid=access_rights_uid)
                if args:
                    # Perform extended search
                    base_domain = args or []
                    for a in base_domain:
                        if isinstance(a, list) and len(a) == 3:
                            new_sub_domain = \
                                _extend_search_results_translation(self, a)
                            a = new_sub_domain
                    new_result = self._search.origin(
                        self, args=base_domain, offset=offset,
                        limit=limit, order=order,
                        count=count, access_rights_uid=access_rights_uid)
                    if not isinstance(result, list):
                        if not isinstance(result, long):
                            result = [result]
                    if not isinstance(new_result, list):
                        if not isinstance(new_result, long):
                            new_result = [new_result]
                    if isinstance(result, list) and \
                            isinstance(new_result, list):
                        result_add = [x for x in new_result if x not in result]
                        if result_add:
                            result.extend(result_add)
                return result
            return _search

        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [])
        for model in self.browse(cr, SUPERUSER_ID, ids):
            Model = self.pool.get(model.model)
            if Model:
                Model._patch_method('name_search', make_name_search())
                Model._patch_method('_search', make_search())
        return super(ModelExtended, self)._register_hook(cr)

# @api.model
# def name_search(self, name='', args=None, operator='ilike', limit=100):
#     result = self._name_search(name, args, operator, limit=limit)
#     if not result:
#         trans_name = '%s,%s' % (self._model, 'name')
#         translation_ids =\
#             self.env['ir.translation'].search([('value', 'ilike', name),
#                                                ('name', '=', trans_name)],
#                                               limit=limit)
#         record_ids = [t.res_id for t in translation_ids]
#         record_ids = self.browse(record_ids)
#         disp = ''
#         for rec in record_ids:
#             if rec:
#                 disp = str(rec.name)
#                 result.append((rec.id, disp))
#     return result
#
# BaseModel.name_search = name_search
