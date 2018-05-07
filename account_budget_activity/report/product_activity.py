# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class ProductActivity(models.Model):
    _name = 'product.activity'
    _auto = False

    temp_activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    temp_product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    name = fields.Char(
        string='Name',
    )

    def _get_sql_view(self):
        sql_view = """
        select id, temp_product_id, temp_activity_id, name
        from ((
            select 1000000 + p.id id,
            p.id temp_product_id, null::int temp_activity_id,
            p.name_template as name
            from product_product p)
        union all (
            select 2000000 + a.id,
            null::int temp_product_id, a.id temp_activity_id,
            a.name as name
            from account_activity a
        )) product_activity
        order by id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
