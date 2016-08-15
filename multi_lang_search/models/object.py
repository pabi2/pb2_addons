# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import tools


# Extended name search is only used on some operators
ALLOWED_OPS = set(['ilike', 'like'])


@tools.ormcache(skiparg=0)
def _get_rec_names(self):
    "List of fields to search into"
    model = self.env['ir.model'].search(
        [('model', '=', str(self._model))])
    rec_name = [self._rec_name] or []
    other_names = model.name_search_ids.mapped('name')
    return rec_name + other_names


def _extend_name_results_translation(self, domain, field_name,
                                     name, results, limit):
    result_count = len(results)
    if result_count < limit:
        domain += [('id', 'not in', [x[0] for x in results])]
        # recs = self.search(domain, limit=limit - result_count)
        trans_name = '%s,%s' % (self._model, field_name)
        translation_ids =\
            self.env['ir.translation'].search([('value', 'ilike', name),
                                               ('name', '=', trans_name)],
                                              limit=limit)
        record_ids = [t.res_id for t in translation_ids]
        record_ids = self.browse(record_ids)
        results.extend(record_ids.name_get())
        results = list(set(results))
    return results


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
                    base_domain = args or []
                    # Try translation word search each of the search fields
                    for rec_name in all_names:
                        domain = [(rec_name, operator, name)]
                        domain = [(rec_name, operator, x)
                                  for x in name.split() if x]
                        res = _extend_name_results_translation(
                            self, base_domain + domain,
                            rec_name, name, res, limit)
                return res
            return name_search

        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [])
        for model in self.browse(cr, SUPERUSER_ID, ids):
            Model = self.pool.get(model.model)
            if Model:
                Model._patch_method('name_search', make_name_search())
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
