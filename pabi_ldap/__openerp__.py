# -*- coding: utf-8 -*-
{
    'name': "NSTDA-BASE :: LDAP",
    'description': """LDAP Configuration
    """,
    'author': 'Jakkrich.cha,Thapanat.sop',
    'category': 'NSTDA-BASE',
    'depends': ['base', 'base_setup', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/users_ldap_view.xml',
    ],
    'qweb': [
        "static/src/xml/auth_cas.xml"
    ],
    'installable': True,
    'external_dependencies': {
        'python': ['ldap'],
    }
}
