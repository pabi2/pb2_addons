# -*- coding: utf-8 -*-

import logging
from openerp.osv import fields, osv
_logger = logging.getLogger(__name__)


class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    _columns = {
        'property_tax_move_by_taxbranch': fields.boolean(
            string='Tax Account Move by Tax Branch',
        ),
        'property_wht_taxbranch_id': fields.many2one(
            'res.taxbranch',
            string='Taxbranch for Withholding Tax',
        ),
    }
    _defaults = {
        'property_tax_move_by_taxbranch': True
    }

    def set_default_tax_move_by_taxbranch(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids)[0]
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        record = ('property_tax_move_by_taxbranch', 'res.partner')
        value = getattr(wizard, record[0])
        field = field_obj.search(
            cr, uid, [
                ('name', '=', record[0]), ('model', '=', record[1])],
            context=context)
        vals = {
            'name': record[0],
            'company_id': False,
            'fields_id': field[0],
            'type': 'boolean',
            'value': value and '1' or '0',
        }
        property_ids = property_obj.search(
            cr, uid, [('name', '=', record[0])], context=context)
        if property_ids:
            # the property exist: modify it
            property_obj.write(cr, uid, property_ids, vals, context=context)
        else:
            # create the property
            property_obj.create(cr, uid, vals, context=context)
        return True

    def get_default_tax_move_by_taxbranch(self, cr, uid, fields, context=None):
        ir_property_obj = self.pool.get('ir.property')
        res = {}
        # for record in todo_list:
        prop = ir_property_obj.get(
            cr, uid,
            'property_tax_move_by_taxbranch', 'res.partner',
            context=context)
        res.update({'property_tax_move_by_taxbranch': prop})
        return res

    def set_default_wht_taxbranch_id(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids)[0]
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        todo_list = [
            ('property_wht_taxbranch_id',
             'res.partner', 'res.taxbranch'),
        ]
        for record in todo_list:
            account = getattr(wizard, record[0])
            value = account and 'res.taxbranch,' + str(account.id) or False
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

    def get_default_wht_taxbranch_id(self, cr, uid,
                                     fields, context=None):
        ir_property_obj = self.pool.get('ir.property')
        todo_list = [
            ('property_wht_taxbranch_id', 'res.partner'),
        ]
        res = {}
        for record in todo_list:
            prop = ir_property_obj.get(cr, uid,
                                       record[0], record[1], context=context)
            print prop
            prop_id = prop and prop.id or False
            res.update({record[0]: prop.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
