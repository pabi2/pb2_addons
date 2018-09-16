# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import except_orm, Warning as UserError
import types


def str2tuple(s):
    return eval('tuple(%s)' % (s or ''))


class IrTestAction(models.TransientModel):
    _name = "ir.test.action"
    _description = "Test Action"

    model = fields.Char(
        string='Object',
        size=500,
        help="Model name on which the method to be called "
        "is located, e.g. 'res.partner'.",
    )
    function = fields.Char(
        string='Method',
        size=500,
        help="Name of the method to be called.",
    )
    args = fields.Text(
        string='Arguments',
        size=1000,
        help="Arguments to be passed to the method, e.g. (uid,).",
    )
    state = fields.Selection(
        [('new', 'New'), ('ok', 'Ok')],
        string='State',
        default='new',
    )
    message = fields.Char(
        string='Message',
        size=500,
    )

    def _check_args(self, cr, uid, ids, context=None):
        try:
            for this in self.browse(cr, uid, ids, context):
                str2tuple(this.args)
        except Exception:
            return False
        return True

    _constraints = [
        (_check_args,
         "Invalid arguments, must be tuple, i.e., "
         "([1], {'name': 'ABC', 'value': 'XYZ'}, 12)",
         ['args']),
    ]

    @api.model
    def _callback(self, model_name, method_name, args):
        args = str2tuple(args)
        registry = openerp.registry(self._cr.dbname)
        res = {}
        if model_name in registry:
            model = registry[model_name]
            if hasattr(model, method_name):
                if len(args) > 9:
                    raise UserError(_('Method with more than 9 arguments '
                                      'is not allowed!'))
                if len(args) == 0:
                    res = getattr(model, method_name)(self._cr, self._uid)
                if len(args) == 1:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0])
                if len(args) == 2:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1])
                if len(args) == 3:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2])
                if len(args) == 4:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2],
                        args[3])
                if len(args) == 5:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2],
                        args[3], args[4])
                if len(args) == 6:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2],
                        args[3], args[4], args[5])
                if len(args) == 7:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2],
                        args[3], args[4], args[5], args[6])
                if len(args) == 8:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2],
                        args[3], args[4], args[5], args[6], args[7])
                if len(args) == 9:
                    res = getattr(model, method_name)(
                        self._cr, self._uid, args[0], args[1], args[2],
                        args[3], args[4], args[5], args[6], args[7], args[8])
            else:
                raise UserError(_("Method '%s.%s' does not exist.") %
                                (model_name, method_name))
        else:
            raise UserError("Model '%s' does not exist." % model_name)

        return res

    @api.multi
    def execute(self):
        res = self._callback(self.model, self.function, self.args)

        message = self._get_message(res)

        if message:
            self.write({'state': 'ok',
                        'message': message})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.test.action',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.model
    def _get_message(self, res):
        message = False
        # Boolean
        if isinstance(res, types.BooleanType):
            if res is True:
                message = _('Last execution was successful!')

        if isinstance(res, types.DictType):
            # Generic
            if 'is_success' in res:
                if res.get('is_success', False):
                    message = _('Last execution was successful!')
                # Failure, show message
                else:
                    message = False
                    if res.get('messages', False):
                        for msg in res.get('messages', False):
                            if message:
                                message += '\n' + msg
                            else:
                                message = msg
                        raise except_orm(_('Validation Error'),
                                         _(message))
                    elif res.get('exception', False):
                        raise except_orm(_('Exception Error'),
                                         _(res.get('exception', False)))
            # Budget Check
            if 'budget_ok' in res:
                message = res
        return message
