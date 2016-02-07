# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    _columns = {
        'property_retention_on_payment':
            fields.boolean('Retention on Payment'),
        'property_account_retention_customer':
            fields.many2one('account.account', 'Account Retention Customer',
                            domain="[('type', '!=', 'view')]",),
        'property_account_retention_supplier':
            fields.many2one('account.account', 'Account Retention Supplier',
                            domain="[('type', '!=', 'view')]",),
    }
    _defaults = {
        'property_retention_on_payment': False
    }

    def set_default_retention_on_payment(self, cr, uid, ids, context=None):
        """ set property retention account for customer and supplier """
        wizard = self.browse(cr, uid, ids)[0]
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        record = ('property_retention_on_payment', 'res.partner')
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

    def set_default_account_retention(self, cr, uid, ids, context=None):
        """ set property retention account for customer and supplier """
        wizard = self.browse(cr, uid, ids)[0]
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        todo_list = [
            (
                'property_account_retention_customer',
                'res.partner', 'account.account'),
            (
                'property_account_retention_supplier',
                'res.partner', 'account.account'),
        ]
        for record in todo_list:
            account = getattr(wizard, record[0])
            value = account and 'account.account,' + str(account.id) or False
            if value:
                field = field_obj.search(
                    cr, uid, [
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

    def get_default_account_retention(self, cr, uid, fields, context=None):
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        todo_list = [
            ('property_account_retention_customer', 'res.partner'),
            ('property_account_retention_supplier', 'res.partner'),
        ]
        res = {}
        for record in todo_list:
            prop = ir_property_obj.get(cr, uid,
                                       record[0], record[1], context=context)
            prop_id = prop and prop.id or False
            account_id = fiscal_obj.map_account(cr, uid, False, prop_id)
            res.update({record[0]: account_id})
        return res

    def get_default_retention_on_payment(self, cr, uid, fields, context=None):
        ir_property_obj = self.pool.get('ir.property')
        res = {}
        # for record in todo_list:
        prop = ir_property_obj.get(
            cr, uid,
            'property_retention_on_payment', 'res.partner',
            context=context)
        res.update({'property_retention_on_payment': prop})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
