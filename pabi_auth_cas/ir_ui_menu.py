# import base64
import operator
# import re
# import threading

# import openerp.modules
from openerp.osv import fields, osv
from openerp import tools
# from openerp.tools.safe_eval import safe_eval as eval
# from openerp.tools.translate import _

MENU_ITEM_SEPARATOR = "/"


class ir_ui_menu(osv.osv):
    _name = 'ir.ui.menu'
    _inherit = 'ir.ui.menu'

    _columns = {
        'app3digi': fields.char('App Menu'),
    }

    def get_user_roots(self, cr, uid, context=None):
        """ Return all root menu ids visible for the user.
        :return: the root menu ids
        :rtype: list(int)
        """
        menu_domain = [('parent_id', '=', False)]
        if context.get('menu', None):
            menu_domain.append(('name', '=', context.get('menu')))

        return self.search(cr, uid, menu_domain, context=context)

#     @api.cr_uid_context
#     @tools.ormcache_context(accepted_keys=('lang',))
    def load_menu(self, cr, uid, context=None):
        """ Loads all menu items (all applications and their sub-menus).

        :return: the menu root
        :rtype: dict('children': menu_nodes)
        """
        fields = ['name', 'sequence', 'parent_id', 'action']
        menu_root_ids = self.get_user_roots(cr, uid, context=context)
        menu_roots = menu_root_ids and \
            self.read(cr, uid, menu_root_ids, fields, context=context) or []
        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': menu_roots,
            'all_menu_ids': menu_root_ids,
        }
        if not menu_roots:
            return menu_root

        # menus are loaded fully unlike a regular tree view, cause there are a
        # limited number of items (752 when all 6.1 addons are installed)
        menu_ids = self.search(
            cr, uid, [('id', 'child_of', menu_root_ids)],
            0, False, False, context=context)
        menu_items = self.read(cr, uid, menu_ids, fields, context=context)
        # adds roots at the end of the sequence, so that they will overwrite
        # equivalent menu items from full menu read when put into id:item
        # mapping, resulting in children being correctly set on the roots.
        menu_items.extend(menu_roots)
        menu_root['all_menu_ids'] = menu_ids  # includes menu_root_ids!

        # make a tree using parent_id
        menu_items_map = dict(
            (menu_item["id"], menu_item) for menu_item in menu_items)
        for menu_item in menu_items:
            if menu_item['parent_id']:
                parent = menu_item['parent_id'][0]
            else:
                parent = False
            if parent in menu_items_map:
                menu_items_map[parent].setdefault(
                    'children', []).append(menu_item)

        # sort by sequence a tree using parent_id
        for menu_item in menu_items:
            menu_item.setdefault('children', []).sort(
                key=operator.itemgetter('sequence'))

        return menu_root

    @tools.ormcache()
    def get_id_by_name(self, cr, uid, app):
        """Returns (model, res_id) corresponding to a given module
        and xml_id (cached) or raise ValueError if not found"""
        app_id = self.search(
            cr, uid, [('app3digi', '=', app),
                      ('parent_id', '=', False)], limit=1)
        if app_id:
            res = self.read(cr, uid, app_id, ['id'])[0]
            if not res['id']:
                raise ValueError(
                    'No such Menu Item currently defined in the system: %s'
                    % (app))
            return res['id']
        else:
            raise ValueError(
                'No such Menu Item currently defined in the system: %s'
                % (app))

    @tools.ormcache()
    def get_name_by_3digi(self, cr, uid, app):
        """Returns (model, res_id) corresponding to a given module and xml_id
        (cached) or raise ValueError if not found"""
        app_id = self.search(
            cr, uid, [('app3digi', '=', app),
                      ('parent_id', '=', False)], limit=1)
        if app_id:
            res = self.read(cr, uid, app_id, ['name'])[0]
            if not res['name']:
                return False
            return res['name']
        else:
            raise False

#     _columns = {
#         'app3digi': fields.char('App Menu'),
#     }
