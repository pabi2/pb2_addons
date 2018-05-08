# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiMonthlyWorkAcceptanceReport(models.Model):
    _name = 'pabi.monthly.work.acceptance.report'
    _description = 'Pabi Monthly Work Acceptance Report'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT
        po.operating_unit_id,
        (SELECT value
        FROM ir_translation
        WHERE res_id = ro.id AND name LIKE 'res.org,name') ou_code,
        CONCAT(CASE to_char(ap.date_start,'MM')
        WHEN '01' THEN 'มกราคม'
        WHEN '02' THEN 'กุมภาพันธ์'
        WHEN '03' THEN 'มีนาคม'
        WHEN '04' THEN 'เมษายน'
        WHEN '05' THEN 'พฤษภาคม'
        WHEN '06' THEN 'มิถุนายน'
        WHEN '07' THEN 'กรกฎาคม'
        WHEN '08' THEN 'สิงหาคม'
        WHEN '09' THEN 'กันยายน'
        WHEN '10' THEN 'ตุลาคม'
        WHEN '11' THEN 'พฤศจิกายน'
        WHEN '12' THEN 'ธันวาคม'
        END,' ',
        EXTRACT(year FROM ap.date_start + interval '543 years')) month_name,
        ap.id order_month,
        (SELECT CONCAT('['||TRIM(rproj.code)||']',' ',rproj.name)
        FROM purchase_order_line pol
        LEFT JOIN res_project rproj
        ON rproj.id = pol.project_id
        WHERE pol.order_id = po.id LIMIT 1) project,
        (SELECT CONCAT('['||TRIM(rs.code)||']',' ',rs.name)
        FROM purchase_order_line pol
        LEFT JOIN res_section rs
        ON rs.id = pol.section_id
        WHERE pol.order_id = po.id LIMIT 1) section,
        CONCAT(
        COALESCE((SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT rpt.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        LEFT JOIN res_partner_title rpt
        ON rpt.id = he.title_id
        WHERE ru.id = pd.request_uid) AND
            it.name LIKE 'res.partner.title,name') || ' ', ''),
        (SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT he.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        WHERE ru.id = pd.request_uid) AND
            it.name LIKE 'hr.employee,first_name'),
        ' ',
        (SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT he.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        WHERE ru.id = pd.request_uid) AND it.name LIKE 'hr.employee,last_name')
        ) as requested_by,
        po.name po_name,
        po.date_order po_date_order,
        pm.name as method,
        CONCAT((SELECT pt.name FROM purchase_type pt
            WHERE pt.id = pd.purchase_type_id),' ',pd.objective) reason,
        po.amount_total,
        rc.name currency,
        CONCAT(COALESCE(rpt.name || ' ',''),rp.name) as supplier_name,
        pd.date_doc_approve
        FROM purchase_order po
        LEFT JOIN purchase_requisition pd
        ON pd.name = po.origin
        LEFT JOIN purchase_method pm
        ON pd.purchase_method_id = pm.id
        LEFT JOIN res_partner rp
        ON po.partner_id = rp.id
        LEFT JOIN res_partner_title rpt
        ON rpt.id = rp.title
        LEFT JOIN res_currency rc
        ON rc.id = po.currency_id
        LEFT JOIN account_period ap
        ON ap.code = to_char(po.date_order,'mm/YYYY')
        LEFT JOIN res_org ro
        ON ro.id = (SELECT DISTINCT pol.org_id
        FROM purchase_order_line pol
        WHERE pol.order_id = po.id)
        WHERE po.order_type LIKE 'purchase_order'
        )""" % (self._table, ))
