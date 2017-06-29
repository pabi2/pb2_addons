var QueryString = function () {
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
    	// If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = pair[1];
    	// If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]], pair[1] ];
      query_string[pair[0]] = arr;
    	// If third or later entry with this name
    } else {
      query_string[pair[0]].push(pair[1]);
    }
  } 
  return query_string;
  
} ();

openerp.e3z_auth_cas = function(instance) {
    var QWeb = instance.web.qweb,
        _t = instance.web._t;
    
    // Used for CAS authentication
    instance.web.Login = instance.web.Login.extend({
        start: function () {
            var self = this;
            this.module_list = instance._modules.slice();
            this.module_loaded = {};
            _(this.module_list).each(function (mod) {
                self.module_loaded[mod] = true;
            });

            // If the url contains 'without_cas', we don't do anything
            // There is a bug if portal_anonymous is activated and there is no session, so we don't do anything in this case too
            if (location.search.lastIndexOf('without_cas') != -1 || (self.module_loaded['portal_anonymous'] && !this.session.username)){
                this._super();
            }
            else {
                self.$('.oe_login_pane').hide();
                return $.when(self._super()).done(function () {
                    var dblist = self.db_list || [];
                    var dbname = self.params.db || (dblist.length === 1 ? dblist[0] : null);
                    if (dbname) {
                        // We get CAS parameters (host, port...)
                        self.rpc("/e3z_auth_cas/get_config", {dbname: dbname})
                            .done(function (result) {
                                // We verify if the CAS authentication is enabled
                                //if (result.login_cas == 'True') {
                            	if (QueryString.adminlogin == undefined) {
                                    self.show_error(_t("CAS authentication in progress"));
                                    var ticket = self.getCASTicket();
                                    if (!ticket)
                                        self.do_redirect(result.host, result.port);
                                    else {
                                        self.rpc("/e3z_auth_cas/cas_authenticate", {
                                        	dbname: dbname,
                                            cur_url: self.delCASTicket(),
                                            cas_host: result.host,
                                            cas_port: result.port,
                                            auto_create: result.auto_create,
                                            ticket: ticket})
                                            .done(function (res) {
                                                // The ticket is invalid, probably because it is not the first time the CAS server checks it
                                                if (res.status != 0) {
                                                    self.show_error(_t("Invalid ticket, you will be redirected in a few seconds."));
                                                    self.do_warn(_t("Invalid ticket"), _t("The ticket is not valid, this page will be redirected in a few seconds. If the problem persist, please contact your administrator."));
                                                    setTimeout(function () {
                                                        self.do_redirect(result.host, result.port);
                                                    }, 500);
                                                }
                                                // When auto_create param is disabled, a user successfully authenticated by CAS
                                                // who doesn't have an account on OpenERP can't login
                                                else if (res.fail) {
                                                    self.show_error(_t("Wrong login, you have no account on OpenERP."));
                                                    self.do_warn(_t("Wrong login"), _t("You must have an account on OpenERP in order to authenticate. Please contact your administrator."));
                                                }
                                                // All is fine, the session cookie is created
                                                else {
                                                    self.session.set_cookie('session_id', res.session_id);
                                                    // admin url
                                                    //var adminURL = window.location.protocol + "//" + window.location.host;
													var adminURL = window.location.protocol + "//" + window.location.host + window.location.pathname + window.location.search.replace("&ticket="+ticket, "");
                                                    window.location.replace(adminURL);
                                                }
                                            });
                                    }
                                }
                                // If the CAS authentication is disabled, we show the standard login page
                                else
                                    self.$('.oe_login_pane').show();
                            		self.$('.oe_signup_signup').hide();
                            		self.$('.oe_signup_reset_password').hide();
                            });
                    }
                });
            }
        },

        // Redirects to CAS server
        do_redirect: function(host, port) {
            var self = this,
                callback_host = self.delCASTicket(),
                host_to_redirect = host + '/login?service=' + encodeURIComponent(callback_host); // mdev-cas-edit
                //host_to_redirect = host + ':' + port + '/login?service=' + encodeURIComponent(callback_host);
			$(location).attr('href', host_to_redirect);
        },

        // Get the ticket from url
        getCASTicket: function() {
            var params = location.search.substring(1).split('&'),
                ticket = false;
            for (var i=0; i<params.length; i++) {
                var arg = params[i].split('=');
                if(arg[0] == ('ticket'))
                    ticket = arg[1];
            }
            return ticket;
        },

        // Delete the ticket from url
        delCASTicket: function() {
            var params = location.search.substring(1).split('#')[0].split('&');
            if($(location).attr('href').lastIndexOf('#') == $(location).attr('href').length - 1) {
                var sharp = true;
            }
            if(location.search == '' || $(location).attr('href').split('?')[1] == '') {
                if(sharp)
                    return $(location).attr('href').split('#')[0].split('?')[0];
                else
                    return $(location).attr('href').split('?')[0] + document.location.hash;
            }
            if(params.length == 1 && params[0].substring(0,6) == 'ticket') {
                if(sharp)
                    return $(location).attr('href').split('#')[0].split('?')[0];
                else
                    return $(location).attr('href').split('?')[0] + document.location.hash;
            }

            var url = $(location).attr('href').split('?')[0] + '?',
                loop = 0;
            for (var i=0; i<params.length; i++) {
                var arg = params[i].split('=');
                if(arg[0] != ('ticket')) {
                    if(loop != 0)
                        url += '&';
                    url += arg[0] + '=' + arg[1];
                    loop++;
                }
            }
            if(sharp)
                return url.split('#')[0];
            else
                return url + document.location.hash;
        }
    });

    // Used for CAS deauthentication
    instance.web.WebClient = instance.web.WebClient.extend({
        on_logout: function() {
            var self = this;
            var dbname;

            // Get the name of the database used
            self.rpc("/web/database/get_list", {})
                .done(function(result) {
                    dbname = result[0];
                    // Logout the user
                    if (!self.has_uncommitted_changes()) {
                        self.session.session_logout().done(function () {
                            $(window).unbind('hashchange', self.on_hashchange);
                            self.do_push_state({});

                            if (dbname) {
                                self.rpc("/e3z_auth_cas/get_config", {dbname: dbname})
                                    .done(function(result) {
                                        // If the CAS authentication is enabled, logout from CAS server too
                                        if(result.login_cas == 'True')
                                            self.cas_logout(result.host, result.port);
                                        else
                                            window.location.reload();
                                    });
                            }
                        });
                    }
                });
        },

        // Logout from CAS server
        cas_logout: function(host, port) {
            var callback_host = $(location).attr('href'),
            host_to_redirect = window.location.protocol + "//" + window.location.host + "/?adminlogin="
            //host_to_redirect = "https://i.nstda.or.th/c/portal/logout?service=" + encodeURIComponent(callback_host);
            //host_to_redirect = host + '/logout?service=' + encodeURIComponent(callback_host);
            $(location).attr('href', host_to_redirect);
        }
    });

    // Used for show information messages when user check CAS parameters
    instance.web.CrashManager = instance.web.CrashManager.extend({
        show_warning: function(error) {
            if (!this.active) {
                return;
            }
            if(error.data.fault_code.lastIndexOf('cas_check_success') != -1 ||
                error.data.fault_code.lastIndexOf('cas_check_fail') != -1) {
                var crashType = error.data.fault_code.split('\n')[0],
                    title = error.data.fault_code.split(crashType)[1].split('\n')[2];
                error.data.fault_code = error.data.fault_code.split(crashType)[1].split('\n')[3];
            }
            else {
                var crashType = 'warning'
                    title = "OpenERP " + _.str.capitalize(error.type);
            }
            instance.web.dialog($('<div>' + QWeb.render('CrashManager.' + crashType, {error: error}) + '</div>'), {
                title: title,
                buttons: [
                    {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
                ]
            });
        }
    });
};