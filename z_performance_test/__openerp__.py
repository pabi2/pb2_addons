# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: Performance Test",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "description": """

This module contain some sample of testing technique.

1) Using Locust for performance testing,
https://github.com/nseinlet/OdooLocust
> locust -f locust_create_so.py Seller
Go to http://localhost:8080 then start the stress test.

2) main.py, by intalling this module, we have option to test http,
   this will out put to log file, lc_report.txt
   Config params
   - report_locust.filepath = /home/kittu/Desktop/
   - report_locust.active = True
   - report_locust.seconds = 1.0

3) test_create_so.py is a simple test script using XMLRPC

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitit U.,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'base',
        'web',
    ],
    "data": [
    ]
}
