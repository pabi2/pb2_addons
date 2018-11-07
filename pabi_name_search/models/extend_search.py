# -*- coding: utf-8 -*-
import re
from openerp import models, api


class ExtendSearch(object):

    @api.model
    def _search_name_to_ids(self, field, value):
        """ name search can as complex, i.e., PV001-PV005,PV006,PV007 """
        # Commas
        values = [x.lower() for x in value.split(',')]
        ex_values = []
        _ids = []
        for n in values:
            if '-' in n:  # case between
                i = n.index('-')  # first occurance of -, split to from and to
                from_number = n[:i]
                to_number = n[i + 1:]
                # Index of occurance of number
                from_prefix = to_prefix = False
                from_suffix = to_suffix = False
                from_padding = to_padding = 0
                # From
                num_index = re.search("\d", from_number)
                if num_index:
                    from_prefix = from_number[:num_index.start()]
                    from_suffix = from_number[num_index.start():]
                    from_padding = len(from_suffix)
                # To
                num_index = re.search("\d", to_number)
                if num_index:
                    to_prefix = to_number[:num_index.start()]
                    to_suffix = to_number[num_index.start():]
                    to_padding = len(to_suffix)
                # Prefix is same, and suffix are both numeric
                if from_prefix and to_prefix and from_prefix == to_prefix and \
                        from_suffix.isdigit() and to_suffix.isdigit() and \
                        from_padding == to_padding:
                    from_digit = int(from_suffix)
                    to_digit = int(to_suffix)
                    for x in range(from_digit, to_digit + 1):
                        y = from_prefix + str(x).zfill(from_padding)
                        ex_values.append(y.lower())
        values_str = "('%s')" % "','".join(values or ['n/a'])
        ex_values_str = "('%s')" % "','".join(ex_values or ['n/a'])
        # Search for value, values and ex_values
        self._cr.execute("""
            select id from %s
            where %s ilike '%s'
            or lower(%s) in %s
            or lower(%s) in %s
        """ % (self._table,
               field, '%%%s%%' % value,
               field, values_str,
               field, ex_values_str))
        _ids += map(lambda x: x[0], self._cr.fetchall())
        return _ids

    @api.model
    def _extend_search_arg(self, args):
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                (field, oper, name) = arg
                if oper == 'ilike' and self._fields[field].type == 'char':
                    _ids = self._search_name_to_ids(field, name)
                    new_args.append(['id', 'in', _ids])
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)
        return new_args


class AccountVoucher(ExtendSearch, models.Model):
    _inherit = 'account.voucher'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(AccountVoucher, self).search(args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)

# CAN NOT USE, conflict with search for all_purchase in pabi_asset_management
# class AccountInvoice(ExtendSearch, models.Model):
#     _inherit = 'account.invoice'
#
#     @api.model
#     def search(self, args, offset=0, limit=None, order=None, count=False):
#         # if self._context.get('extended_search', False):
#         args = self._extend_search_arg(args)
#         return super(AccountInvoice, self).search(args, offset=offset,
#                                                   limit=limit, order=order,
#                                                   count=count)


class AccounMove(ExtendSearch, models.Model):
    _inherit = 'account.move'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(AccounMove, self).search(args, offset=offset,
                                              limit=limit, order=order,
                                              count=count)


class AccounMoveLine(ExtendSearch, models.Model):
    _inherit = 'account.move.line'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(AccounMoveLine, self).search(args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)


class ChartfieldView(ExtendSearch, models.Model):
    _inherit = 'chartfield.view'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(ChartfieldView, self).search(args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)


class ResSection(ExtendSearch, models.Model):
    _inherit = 'res.section'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(ResSection, self).search(args, offset=offset,
                                              limit=limit, order=order,
                                              count=count)


class ResInvestAsset(ExtendSearch, models.Model):
    _inherit = 'res.invest.asset'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(ResInvestAsset, self).search(args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)


class ResProject(ExtendSearch, models.Model):
    _inherit = 'res.project'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(ResProject, self).search(args, offset=offset,
                                              limit=limit, order=order,
                                              count=count)


class ResInvesetConstruction(ExtendSearch, models.Model):
    _inherit = 'res.invest.construction'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # if self._context.get('extended_search', False):
        args = self._extend_search_arg(args)
        return super(ResInvesetConstruction, self).search(args, offset=offset,
                                                          limit=limit,
                                                          order=order,
                                                          count=count)
