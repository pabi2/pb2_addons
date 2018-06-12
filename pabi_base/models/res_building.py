# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class BCommon(object):
    """ Building Common Fields """

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            result.append((rec.id, "%s%s" %
                           (rec.code and '[' + rec.code + '] ' or '',
                            name or '')))
        return result

    # Domain name_search
    # This is a required variable, if any object with ResCommon needs to domain
    # They need to have context in view
    _building_name_search_list = []

    @api.model
    def _add_name_search_domain(self):
        """ Additiona domain for context's name serach """
        domain = []
        ctx = self._context.copy()
        for i in self._building_name_search_list:
            domain += [(i, '=', ctx.get(i))]
        return domain

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if args is None:
            args = []
        args += self._add_name_search_domain()
        return super(BCommon, self).name_search(name=name, args=args,
                                                operator=operator,
                                                limit=limit)

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0,
    #                 limit=None, order=None):
    #     if domain is None:
    #         domain = []
    #     domain += self._add_name_search_domain()
    #     res = super(BCommon, self).search_read(domain=domain, fields=fields,
    #                                            offset=offset, limit=limit,
    #                                            order=order)
    #     return res
    #
    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None,
    #                orderby=False, lazy=True):
    #     if domain is None:
    #         domain = []
    #     domain += self._add_name_search_domain()
    #     res = super(BCommon, self).read_group(domain, fields, groupby,
    #                                           offset=offset, limit=limit,
    #                                           orderby=orderby, lazy=lazy)
    #     return res


class ResBuilding(BCommon, models.Model):
    _name = 'res.building'
    _description = 'Building'

    floor_ids = fields.One2many(
        'res.floor',
        'building_id',
        string='Floors',
    )

    @api.model
    def _check_room_location(self, building, floor, room):
        """ Ensure that room / floor / building are in good combination """
        if (room and (not building or not floor)) or \
                (floor and not building):
            raise ValidationError(
                _('Invalid selection of building/floor/room'))
        if floor and floor not in building.floor_ids:
            raise ValidationError(
                _('Selected floor %s is not in building %s') %
                (floor.name, building.name))
        if room and room not in floor.room_ids:
            raise ValidationError(
                _('Selected room %s is not in floor %s building %s') %
                (room.name, floor.name, building.name))


class ResFloor(BCommon, models.Model):
    _name = 'res.floor'
    _description = 'Floor'
    _building_name_search_list = ['building_id']

    building_id = fields.Many2one(
        'res.building',
        string='Building',
        required=True,
        index=True,
    )
    room_ids = fields.One2many(
        'res.room',
        'floor_id',
        string='Rooms',
    )


class ResRoom(BCommon, models.Model):
    _name = 'res.room'
    _description = 'Room'
    _building_name_search_list = ['building_id', 'floor_id']

    floor_id = fields.Many2one(
        'res.floor',
        string='Floor',
        required=True,
        index=True,
    )
    building_id = fields.Many2one(
        'res.building',
        string='Building',
        related='floor_id.building_id',
        readonly=True,
    )
