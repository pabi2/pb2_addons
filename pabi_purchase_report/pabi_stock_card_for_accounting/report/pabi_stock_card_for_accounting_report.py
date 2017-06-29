# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiStockCardForAccountingReport(models.Model):
    _name = 'pabi.stock.card.for.accounting.report'
    _description = 'Pabi Stock Card For Accounting Report'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT
        ou.id ou_id,
        pp.id product_id,
        pc.id category_id,
        rp.name company_name,
        rp.vat taxid,
        CONCAT(
        COALESCE(rp.street||' ',''),
        COALESCE(rp.street2||' ',''),
        COALESCE((SELECT rct.name FROM res_country_township rct
            WHERE rct.id = rp.township_id)||' ',''),
        COALESCE((SELECT rcd.name FROM res_country_district rcd
            WHERE rcd.id = rp.district_id)||' ',''),
        COALESCE((SELECT rcp.name FROM res_country_province rcp
            WHERE rcp.id = rp.province_id)||' ',''),
        COALESCE(rp.zip,'')
        ) address,
        ou.name plant,
        ptmpl.name product_name,
        pc.name category_name,
        pu.name uom,
        sm.date,
        pwa.name GRGIslip,
        (SELECT sl.operating_unit_id FROM stock_location sl
            WHERE sl.id = sm.location_id) source_location,
        (SELECT sl.operating_unit_id FROM stock_location sl
            WHERE sl.id = sm.location_dest_id) destination_location,
        sm.price_unit,
        sm.product_uom_qty,
        pwal.balance_qty
        FROM stock_move sm
        LEFT JOIN stock_picking sp
        ON sp.id = sm.picking_id
        LEFT JOIN purchase_work_acceptance pwa
        ON pwa.id = sp.acceptance_id
        LEFT JOIN operating_unit ou
        ON ou.id = sp.operating_unit_id
        LEFT JOIN res_partner rp
        ON rp.id = ou.partner_id
        LEFT JOIN product_product pp
        ON pp.id = sm.product_id
        LEFT JOIN product_template ptmpl
        ON ptmpl.id = pp.product_tmpl_id
        LEFT JOIN product_category pc
        ON pc.id = ptmpl.categ_id
        LEFT JOIN product_uom pu
        ON pu.id = ptmpl.uom_po_id
        LEFT JOIN purchase_work_acceptance_line pwal
        ON pwal.acceptance_id = sp.acceptance_id
        WHERE sm.state = 'done'
        )""" % (self._table, ))
