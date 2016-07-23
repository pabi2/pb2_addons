# -*- coding: utf-8 -*-

import logging
from openerp.osv import fields, osv
_logger = logging.getLogger(__name__)


class hr_config_settings(osv.osv_memory):
    _inherit = 'hr.config.settings'
    _columns = {
        'property_employee_advance_product_id': fields.many2one(
            'product.product',
            string='Employee Advance Product',
        ),
    }

    def set_default_employee_advance_product_id(self, cr, uid, ids,
                                                context=None):
        wizard = self.browse(cr, uid, ids)[0]
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        todo_list = [
            ('property_employee_advance_product_id',
             'res.partner', 'product.product'),
        ]
        for record in todo_list:
            account = getattr(wizard, record[0])
            value = account and 'product.product,' + str(account.id) or False
            if value:
                field = field_obj.search(cr, uid, [
                    ('name', '=', record[0]),
                    ('model', '=', record[1]),
                    ('relation', '=', record[2])],
                    context=context)
                vals = {
                    'name': record[0],
                    'company_id': False,
                    'fields_id': field[0],
                    'value': value,
                }
                property_ids = property_obj.search(
                    cr, uid, [('name', '=', record[0])], context=context)
                if property_ids:
                    # the property exist: modify it
                    property_obj.write(
                        cr, uid, property_ids, vals, context=context)
                else:
                    # create the property
                    property_obj.create(cr, uid, vals, context=context)
        return True

    def get_default_employee_advance_product_id(self, cr, uid,
                                                fields, context=None):
        ir_property_obj = self.pool.get('ir.property')
        todo_list = [
            ('property_employee_advance_product_id', 'res.partner'),
        ]
        res = {}
        for record in todo_list:
            prop = ir_property_obj.get(cr, uid, record[0], record[1],
                                       context=context)
            print prop
            res.update({record[0]: prop and prop.id or False})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
