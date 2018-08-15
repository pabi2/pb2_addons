import ldap
from ldap.filter import filter_format
from ldap.controls import SimplePagedResultsControl
from distutils.version import StrictVersion
from time import localtime, strftime, strptime, timezone
from datetime import datetime
import openerp.exceptions
from openerp import pooler
from openerp import tools
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
import string
import random
import logging

import re
import urllib
import urllib2
import base64
import re
_logger = logging.getLogger(__name__)

# Check if we're using the Python "ldap" 2.4 or greater API
LDAP24API = StrictVersion(ldap.__version__) >= StrictVersion('2.4')
# If you're talking to LDAP, you should be using LDAPS for security!
PAGESIZE = 5000


class osv_memory_nstdajob_syncuser(openerp.osv.osv.osv_memory):
    """ Expose the osv_memory.vacuum() method to the cron jobs mechanism. """
    _name = 'osv_memory.nstdajob_syncuser'
    # _auto = False

    def internet_on(self, url):
#         _logger.info('LDAP Detail Image URL: %s' % url)
        try:
            urllib2.urlopen(url, timeout=1)
#             _logger.info('LDAP Detail Image URL OK !!')
            return True
        except urllib2.HTTPError as err:
            _logger.info(err)
            return False
        except urllib2.URLError as err:
            _logger.info(err)
            return False
        except:
            _logger.info('LDAP Detail Image (%s)e Except!!' , (url,))
            return False
        
    def randompassword(self):
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        size = random.randint(8, 12)
        return ''.join(random.choice(chars) for x in range(size))

    def create_controls(self, pagesize):
        # Initialize the LDAP controls for paging. Note that we pass ''
        # for the cookie because on first iteration, it starts out empty.
        if LDAP24API:
            return SimplePagedResultsControl(True, size=pagesize, cookie='')
        else:
            return SimplePagedResultsControl(ldap.LDAP_CONTROL_PAGE_OID, True, (pagesize, ''))

    def get_pctrls(self, serverctrls):
        """Lookup an LDAP paged control object from the returned controls."""
        # Look through the returned controls and find the page controls.
        # This will also have our returned cookie which we need to make
        # the next search request.
        if LDAP24API:
            return [c for c in serverctrls
                    if c.controlType == SimplePagedResultsControl.controlType]
        else:
            return [c for c in serverctrls
                    if c.controlType == ldap.LDAP_CONTROL_PAGE_OID]

    def set_cookie(self, lc_object, pctrls, pagesize):
        """Push latest cookie back into the page control."""
        if LDAP24API:
            cookie = pctrls[0].cookie
            lc_object.cookie = cookie
            return cookie
        else:
            est, cookie = pctrls[0].controlValue
            lc_object.controlValue = (pagesize, cookie)
            return cookie

    # This is essentially a placeholder callback function. You would do your real
    # work inside of this. Really this should be all abstracted into a
    # generator...
    def process_entry(self, dn, attrs):
        """Process an entry. The two arguments passed are the DN and
           a dictionary of attributes."""
        print dn, attrs

    def sync_user(self, cr, uid, arg, context=None):
        body_mail = ""
        c = 0
        error = False
        try_run = False
        #-------------------- Notification --------------------
        body_mail += str(datetime.now()) + " LDAP Job Sync Start" + "<br/>"
        _logger.info("LDAP Job Sync Start")
        baseDN = False
        searchFilter = False
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        
        try:
            body_mail += str(datetime.now()) + " LDAP Job Sync Start DB@" + cr.dbname + "<br/>"
            _logger.info("LDAP Job Sync Start DB@" + cr.dbname)
            ldap_con = pooler.get_pool(cr.dbname).get('res.company.ldap')
            con = ldap_con.get_ldap_dicts(cr)
        except ldap.LDAPError, e:
            body_mail += str(datetime.now()) + " LDAP Job Sync Error: " + e + "<br/>"
            _logger.info("LDAP Job Sync Error: " + e)

        logstr = False
        try:
            for conCenter in con:
                c = 1
                body_mail += str(datetime.now()) + " LDAP Job Sync Center: " + conCenter['ldap_base'] + "<br/>"
                _logger.info("LDAP Job Sync Center: " + conCenter['ldap_base'])
                baseDN = str(conCenter['ldap_base'])
                searchFilter = str(conCenter['ldap_filter'])
                profile_image_sync = conCenter['profile_image_sync']
                profile_image_url = str(conCenter['profile_image_url'])
#                 _logger.info("LDAP Job Sync Connect LDAP Starting")
                l = ldap.open(str(conCenter['ldap_server']))
                l.set_option(ldap.OPT_TIMEOUT, 10)
                l.simple_bind_s(conCenter['ldap_binddn'], conCenter['ldap_password'])
#                 _logger.info("LDAP Job Sync Connect LDAP ")
                l.protocol_version = ldap.VERSION3
                lc = self.create_controls(PAGESIZE)
                ldap_obj = pooler.get_pool(cr.dbname).get('res.company.ldap')
#                 ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
                ldap_result_id = l.search_ext( baseDN, searchScope, searchFilter, retrieveAttributes, serverctrls=[lc])
#                 _logger.info("LDAP Job Sync Start baseDN: " + baseDN)
                try_run = 3
                while try_run > 0:
                    try:
#                         _logger.info('LDAP Result GET...')
                        result_type, result_data = l.result(ldap_result_id, 0)
#                         _logger.info('LDAP Result GET Complete!! result_data: %s' % result_data)
                    except ldap.LDAPError as e:
                        _logger.info('LDAP Result Retry(%s/3) Connect LDAP server' % try_run)
                        try_run -= 1
                        l = ldap.open(str(conCenter['ldap_server']))
                        l.set_option(ldap.OPT_TIMEOUT, 10)
                        l.simple_bind_s(conCenter['ldap_binddn'], conCenter['ldap_password'])
                        l.protocol_version = ldap.VERSION3
                        ldap_result_id = l.search_ext( baseDN, searchScope, searchFilter, retrieveAttributes, serverctrls=[lc])

                    if not result_data:
                        break
                    else:
                        if result_data[0] and re.match(r'\d{6}', result_data[0][1]['sAMAccountName'][0]):
                            mail = str(result_data[0][1]['sAMAccountName'][0]) + '@nstda.or.th'
                            name_eng = 'Unknow'
                            if result_data[0][1].has_key('mail'):
                                mail = result_data[0][1]['mail'][0].lower()

                            if result_data[0][1].has_key('cn'):
                                name_eng = result_data[0][1]['cn'][0]
                            
                            domain = re.search("@[\w.]+", mail)
                            doamin_org = domain.group()
                            logstr = "Sync LDAP TryRun("+ str(try_run) +"/3) " + str(doamin_org).upper() + " : (" + str(c) + ")" + ":" + str(result_data[0][1]['sAMAccountName'][0]) + " Email:" + tools.ustr(mail) + " Name:" + tools.ustr(name_eng)
                            _logger.info(logstr)
                            #--------------------------------------------------
                            user_id = ldap_obj.get_or_create_user(cr, SUPERUSER_ID, conCenter, result_data[0][1]['sAMAccountName'][0], result_data[0])
#                             _logger.info('LDAP Detail sAMAccountName: %s' % str(result_data[0][1]['sAMAccountName'][0]))
                            if user_id:
                                cr.execute("SELECT partner_id FROM res_users WHERE id=%s", (user_id,))
                                res = cr.fetchone()
                                partner_id = res[0]
#                                 _logger.info('LDAP Detail Check Image Sync %s' % str(profile_image_sync))
                                if profile_image_sync:
                                    image = False
#                                     _logger.info('LDAP Detail Check Image URL')
                                    if self.internet_on(profile_image_url + str(result_data[0][1]['sAMAccountName'][0]) + ".jpg"):
                                        image = urllib2.urlopen(profile_image_url + str(result_data[0][1]['sAMAccountName'][0]) + ".jpg").read()
                                    mail = str(result_data[0][1]['sAMAccountName'][0]) + '@nstda.or.th'
                                    name_eng = 'Unknow'
                                    if result_data[0][1].has_key('mail'):
                                        mail = result_data[0][1]['mail'][0].lower()
                                    if result_data[0][1].has_key('cn'):
                                        name_eng = result_data[0][1]['cn'][0]
                                    if image:
                                        cr.execute("""UPDATE res_partner
                                                        SET country_id=219,
                                                        tz=%s,
                                                        email=%s,
                                                        name=%s,
                                                        user_id=%s,
                                                        employee=True,
                                                        notify_email='none',
                                                        image=%s,
                                                        image_medium=%s,
                                                        image_small=%s
                                                         WHERE id=%s""",
                                                   ("Asia/Bangkok",
                                                    tools.ustr(mail),
                                                    tools.ustr(name_eng),
                                                    tools.ustr(user_id),
                                                    base64.b64encode(image),
                                                    base64.b64encode(image),
                                                    base64.b64encode(image),
                                                    tools.ustr(partner_id),))
                                        cr.commit()
                                    else:
                                        cr.execute("""UPDATE res_partner
                                                    SET country_id=219,
                                                    tz=%s,
                                                    email=%s,
                                                    name=%s,
                                                    user_id=%s,
                                                    employee=True,
                                                    notify_email='none'
                                                    WHERE id=%s""",
                                               ("Asia/Bangkok",
                                                tools.ustr(mail),
                                                tools.ustr(name_eng),
                                                tools.ustr(user_id),
                                                tools.ustr(partner_id),))
                                        cr.commit()
                                else:
#                                     _logger.info('LDAP Detail Not Use Image')
                                    cr.execute("""UPDATE res_partner
                                                    SET country_id=219,
                                                    tz=%s,
                                                    email=%s,
                                                    name=%s,
                                                    user_id=%s,
                                                    employee=True,
                                                    notify_email='none'
                                                    WHERE id=%s""",
                                               ("Asia/Bangkok",
                                                tools.ustr(mail),
                                                tools.ustr(name_eng),
                                                tools.ustr(user_id),
                                                tools.ustr(partner_id),))
                                    cr.commit()

                # Clean up
                l.unbind()
                if logstr:
                    body_mail += str(datetime.now()) + logstr + " [Last]<br/>"
        except ldap.LDAPError, e:
            #-------------------- Notification --------------------
            error = True
            cr.execute("""UPDATE ir_cron
                            SET nextcall=now()
                            WHERE name=%s AND function=%s""",
                       ("SyncUser ldap NSTDA All", "sync_user"))
            cr.commit()
            body_mail += str(datetime.now()) + " LDAP Job Sync Fail:" + str(c) + " records \n" + str(e) + "\n baseDN: " + baseDN + "<br/>"
            _logger.error(" LDAP Job Sync Fail:" + str(c) + " records \n" + str(e) + "\n baseDN: " + baseDN)

        if not try_run:
            body_mail += str(datetime.now()) + " LDAP Job Sync Fail Maximum Retry" + "<br/>"
            _logger.error(" LDAP Job Sync Fail Maximum Retry")
            error = True 
             
        if not error:
            #-------------------- Notification --------------------
            body_mail += str(datetime.now()) + " LDAP Job Sync Successful" + "<br/>"
            _logger.info(" LDAP Job Sync Successful:" + str(c) + " records")
        
        if body_mail:
            self.pre_send_mail(cr, uid, body_mail)
        
osv_memory_nstdajob_syncuser()
