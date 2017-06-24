# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiFixedAssetNonStandardReport(models.Model):
    _name = 'pabi.fixed.asset.non.standard.report'
    _description = 'Pabi Fixed Asset Non Standard Report'
    _auto = False

    # purchase_type_id = fields.Many2one(
    #     'purchase.type',
    #     string='Purchase Type',
    # )
    # purchase_method_id = fields.Many2one(
    #     'purchase.method',
    #     string='Purchase Type',
    # )
    # date_from = fields.Date(string='Contract Start Date')
    # date_to = fields.Date(string='Contract End Date')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT
        pp.name_template AS product_name,
        po.name AS po_name,
        pol.price_unit AS pol_price,
        prql.price_unit AS pr_price,
        po.date_order,
        trim(concat(rp.title,' ',rp.name)) AS partner_name,
        rcp.name AS province,
        extract(year from age(aaa.warranty_expire_date,
                              aaa.warranty_start_date))*12 +
        extract(month from age(aaa.warranty_expire_date,
                               aaa.warranty_start_date)) AS warranty,
        aaa.name AS note,
        sm.name AS description
        FROM
        account_asset aaa
        LEFT JOIN product_product pp ON pp.id = aaa.product_id
        LEFT JOIN stock_move sm ON sm.id = aaa.move_id
        LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
        LEFT JOIN purchase_order po ON po.name = sp.origin
        LEFT JOIN res_partner rp ON rp.id = po.partner_id
        LEFT JOIN res_country_province rcp ON rcp.id = rp.province_id
        LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
        LEFT JOIN purchase_requisition_line prl
            ON pol.requisition_line_id = prl.id
        LEFT JOIN purchase_request_purchase_requisition_line_rel prprl
            ON prl.id = purchase_requisition_line_id
        LEFT JOIN purchase_request_line prql
            ON prprl.purchase_request_line_id = prql.id
        WHERE po.order_type = 'purchase_order'
            and prl.is_standard_asset != True
        ORDER BY po.name, pol.id
        )""" % (self._table, ))
