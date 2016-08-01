openerp.pabi_purchase_contract = function(instance) {

	var MODELS_TO_HIDE = [ 'purchase.contract' ];

	var QWeb = instance.web.qweb, _t = instance.web._t, _lt = instance.web._lt;
	var dateBefore = null;

	instance.web.ListView
			.include({
				start : function() {
					var self = this;
					var ret = this._super.apply(this, arguments);
					var res_model = this.dataset.model;

					return ret;
				},

				do_verified_poc : function(ids) {
					if (!(ids.length && confirm(_t("Do you really want to verified these records?")))) {
						return;
					}
					var self = this;
					var ds = new instance.web.DataSet(this, 'purchase.contract');
					return $.when(
							ds.call('action_button_accept_doc_v7', [ ids ]))
							.done(function(data) {
								self.reload();
							});
				},

				do_verified_selected_poc : function() {
					var ids = this.groups.get_selection().ids;
					if (ids.length) {
						this.do_verified_poc(this.groups.get_selection().ids);
					} else {
						this.do_warn(_t("Warning"),
								_t("You must select at least one record."));
					}
				},

				load_list : function() {
					var self = this;
					var tmp = this._super.apply(this, arguments);
					var res_model = this.dataset.model;
					if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
						self.options.importable = false;

						$(document)
								.ajaxStop(
										function() {
											if (self.options.action != null) {
												if (self.options.action.context.verified_view == '1') {
													$(
															'.oe_view_manager_buttons')
															.hide();
												} else {
													$(
															'.oe_view_manager_buttons')
															.show();
												}
											}
										});

						if (self.options.action != null) {
							if (self.options.action.context.verified_view == '1') {
								this.sidebar = new instance.web.Sidebar(this);
								this.sidebar.appendTo(this.options.$sidebar);
								this.sidebar.add_items('other', _.compact([ {
									label : _t('Accept Documents'),
									callback : this.do_verified_selected_poc
								} ]));
								this.sidebar
										.add_toolbar(this.fields_view.toolbar);
								this.sidebar.$el.hide();
								$('.oe_view_manager_buttons').hide();
							} else {
								$(".oe_view_manager_sidebar").remove();
								$(".oe_alternative")
										.css("visibility", "hidden");
							}
						} else {
							$(".oe_view_manager_sidebar").remove();
							$(".oe_alternative").css("visibility", "hidden");
						}

						$('.oe_form_button').bind("click", function() {
							$(this).removeAttr('disabled');
							$(this).css('color', 'rgb(0, 0, 0)');
						});

					}
					;
				},

				on_loaded : function(data, grouped) {
					// tree/@editable takes priority on everything else if
					// present.
					return this._super(data, grouped);
				},
			});

	instance.web.FormView.include({
		start : function() {
			var self = this;
			var ret = this._super.apply(this, arguments);
			var res_model = this.dataset.model;
			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				$('.oe_list_header_columns > th').css('text-align', 'center');
				self.options.importable = false;
				$(".oe_view_manager_sidebar").remove();
			}
			;
			return ret;
		},
		load_form : function() {
			var self = this;
			var tmp = this._super.apply(this, arguments);
			var res_model = this.dataset.model;

			if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
				$(document).tooltip();

				self.options.importable = false;
				$(".oe_view_manager_sidebar").remove();

				$('.oe_view_manager_buttons').show();
				$('.oe_form_button_create').show();

				var button_t = setInterval(function() {
					$('.oe_form_button').bind("click", function() {
						$(this).removeAttr('disabled');
						$(this).css('color', 'rgb(0, 0, 0)');
					});
				}, 500);
			}
			;
		},
	});
}