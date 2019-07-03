# -*- coding: utf-8 -*-
{
    # ----------------------- Edit --------------
    'name': "NSTDA-CONF :: Jasper Report Engine (REST V2)",               # ชื่อระบบ Eng
    'summary': "Jasper Report Engine (REST V2)",                            # ชื่อระบบ Thai
    'description': """ """,
    'website': '',            # เปลี่ยน ตัวย่อ new เป็นของระบบตนเอง
    'depends': ['base'],    # หากมีเพิ่มให้ต่อด้วย ","(comma)
    'data': [
        "security/security.xml",
        "ir_report_view.xml",
        "nstdaconf_report_view.xml",
        "ir_config_parameter.xml",
        "reports/jasper_data.xml",
    ],
    # ----------------------- NOT Edit --------------
    'category': 'NSTDA',
    'author': 'ICT Team',
    'installable': True,
    'auto_install': True,
}
