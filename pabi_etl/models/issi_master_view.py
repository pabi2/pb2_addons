# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools


class ISSIHrEmployee(models.Model):
    _name = 'issi.hr.employee.view'
    _auto = False
    _description = 'HR employee view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
             SELECT e.id,
                e.employee_code,
                e.first_name,
                t.name AS title,
                e.last_name,
                e.work_phone,
                e.mobile_phone,
                o.name AS org_desc,
                s.id AS section_id,
                concat('[', btrim((s.code)::text), '] ', s.name) AS section_desc,
                d.name AS div_name,
                COALESCE(irt.value, (t.name)::text) AS title_th,
                COALESCE(irf.value, (e.first_name)::text) AS first_name_th,
                COALESCE(irl.value, (e.last_name)::text) AS last_name_th,
                COALESCE(iro.value, (o.name)::text) AS org_desc_th,
                concat('[', btrim((s.code)::text), '] ', COALESCE(irs.value, (s.name)::text)) AS section_desc_th,
                COALESCE(ird.value, (d.name)::text) AS div_name_th,
                po.name AS "position",
                COALESCE(irp.value, (po.name)::text) AS position_th,
                e.org_id,
                u.active,
                ((((COALESCE(irt.value, COALESCE((t.name)::text, ''::text)) || ' '::text) || COALESCE(irf.value, (e.first_name)::text)) || ' '::text) || COALESCE(irl.value, (e.last_name)::text)) AS full_name_th,
                (((((COALESCE(t.name, ''::character varying))::text || ' '::text) || (COALESCE(e.first_name, ''::character varying))::text) || ' '::text) || (COALESCE(e.last_name, ''::character varying))::text) AS full_name_en,
                ((((((('['::text || (e.employee_code)::text) || '] '::text) || COALESCE(irt.value, COALESCE((t.name)::text, ''::text))) || ' '::text) || COALESCE(irf.value, (e.first_name)::text)) || ' '::text) || COALESCE(irl.value, (e.last_name)::text)) AS display_name_th,
                ((((((('['::text || (e.employee_code)::text) || '] '::text) || (COALESCE(t.name, ''::character varying))::text) || ' '::text) || (COALESCE(e.first_name, ''::character varying))::text) || ' '::text) || (COALESCE(e.last_name, ''::character varying))::text) AS display_name_en
               FROM (((((((((((((hr_employee e
                 JOIN res_users u ON (((e.employee_code)::text = (u.login)::text)))
                 LEFT JOIN res_org o ON ((e.org_id = o.id)))
                 LEFT JOIN hr_position po ON ((e.position_id = po.id)))
                 LEFT JOIN res_partner_title t ON ((e.title_id = t.id)))
                 LEFT JOIN res_section s ON ((e.section_id = s.id)))
                 LEFT JOIN res_division d ON ((d.id = s.division_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.partner.title,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irt ON ((t.id = irt.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'hr.employee,first_name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irf ON ((e.id = irf.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'hr.employee,last_name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irl ON ((e.id = irl.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.org,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) iro ON ((o.id = iro.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.section,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irs ON ((s.id = irs.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.division,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) ird ON ((d.id = ird.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'hr.position,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irp ON ((po.id = irp.res_id)))
        )
        """ % self._table)
