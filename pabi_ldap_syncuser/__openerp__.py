# -*- coding: utf-8 -*-
{
    'name': "NSTDA-BASE :: Sync LDAP's users",
    'description': """Setup schedule job for Sync LDAP's users  
    """,
    'author': 'Jakkrich.cha,Thapanat',
    'category': 'NSTDA-BASE',
    'depends':  ['base','pabi_ldap'],
    'data':[
        'data/ir_config_parameter.xml',
    ],
    'external_dependencies' : {
        'python' : ['ldap'],
    },
    'installable': True,
    'auto_install': True,
}
