odoo.define('mai_pos_delivery_mode.delivery_mode', function (require) {
"use strict";

var PosBaseWidget = require('point_of_sale.BaseWidget');
var keyboard = require('point_of_sale.keyboard');
var chrome = require('point_of_sale.chrome');
var PopupWidget = require('point_of_sale.popups');
var PosDB = require('point_of_sale.DB');
var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
var core = require('web.core');
var Session = require('web.Session');
var rpc = require('web.rpc');

// var DataModel = require('web.DataModel');
var QWeb = core.qweb;
var _t = core._t;
var load_count = 0;


	var Model=models.load_models({
		model: 'pos.deliverymode',
		fields: ['id','name'],
		loaded: function(self, delivery_mode){
			self.delivery_mode_db = []
			self.current_delivery_mode = {}
			self.delivery_mode_by_name = {}
			for ( var i =0 ;  i <delivery_mode.length; i++){
				self.delivery_mode_db.push(delivery_mode[i])
				self.delivery_mode_by_name[delivery_mode[i].name] = delivery_mode[i]
			}
		}
	});

	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function(session, attributes) {
			return _super_posmodel.initialize.call(this,session,attributes);
		},
		add_new_order: function() {
			 _super_posmodel.add_new_order.apply(this,arguments);
			 $('.delivery_mode').click();
		}
	});

	var DeliveryModeWidget = PopupWidget.extend({
		template: 'DeliveryModeWidget',
		init: function(parent, options){
			options = options || {};
			this._super(parent,options);
		},
		renderElement: function(){
			var self = this;
			this._super();

			this.$el.click(function(){
				self.click_delivery_mode();
			});
			var idletime = this.pos.config.idletime;
			if(idletime>0)
			{
				idletime = idletime * 60000;
				var idleState = false;
				var idleTimer = null;
				$('*').bind('mousemove click mouseup mousedown keydown keypress keyup submit change mouseenter scroll resize dblclick', function () {
					clearTimeout(idleTimer);
					idleState = false;
					idleTimer = setTimeout(function () {
						idleState = true;
						self.gui.select_employee({
							'security':     true,
							'current_employee': self.pos.get_cashier(),
							'title':      _t('Change Cashier'),
						}).then(function(employee){
							self.pos.set_cashier(employee);
							self.chrome.widget.username.renderElement();
							self.renderElement();
						});

					}, idletime);
				});
				$("body").trigger("mousemove");
			}
		},

		select_delivery_mode: function(parent,options){
			options = options || {};
			var self = this;
			var asrImage = {
				'Delivery - Web': '/mai_pos_delivery_mode/static/src/img/DeliveryWeb.png',
				'Delivery - Whats App': '/mai_pos_delivery_mode/static/src/img/DeliveryWhatsapp.png',
				'Delivery - Phone': '/mai_pos_delivery_mode/static/src/img/DeliveryPhone.png',
				'Delivery - HelloFood': '/mai_pos_delivery_mode/static/src/img/DeliveryJF.png',
				'Take Away': '/mai_pos_delivery_mode/static/src/img/TakeAway.png',
				'Dine In': '/mai_pos_delivery_mode/static/src/img/DineIn.png',
			}
			var def  = new $.Deferred();
			var list = [];
			for (var i = 0; i < self.pos.delivery_mode_db.length; i++) {
				var objDeliveryMode = self.pos.delivery_mode_db[i];
				list.push({
					'label': objDeliveryMode.name,
					'item':  objDeliveryMode,
					'image': 'background-image:url('+ asrImage[objDeliveryMode.name]+');'
				});
			};

			if (load_count==0){
				load_count = load_count+1;

				
				self.gui.show_popup('delivery_mode_selection',{
					'title': options.title || 'Select Order Type',
					list: list,
					confirm: function(user){
						var objOrder = self.pos.get_order()
						self.pos.current_delivery_mode[[self.pos.pos_session.id,self.pos.get_order().sequence_number]] = self.pos.delivery_mode_by_name[user.name]
						objOrder.set_delivery_mode(user);
						$('.delivery_mode').text(user.name);
						// document.getElementsByClassName("delivery_mode")[0].innerHTML = user.name
						def.resolve(user); 
					},
					cancel:  function(){ def.reject(); },
				});
			
			}
			else{
				self.gui.show_popup('delivery_mode_selection',{
				'title': options.title || 'Select Order Type',
				list: list,
				confirm: function(user){
					var objOrder = self.pos.get_order()
					self.pos.current_delivery_mode[[self.pos.pos_session.id,self.pos.get_order().sequence_number]] = self.pos.delivery_mode_by_name[user.name]
					objOrder.set_delivery_mode(user);
					$('.delivery_mode').text(user.name);
					// document.getElementsByClassName("delivery_mode")[0].innerHTML = user.name
					def.resolve(user); 
				 },
				cancel:  function(){ def.reject(); },
				});
			}
		},

		get_mode: function(){
			var order = this.pos.get_order();
			var str_current_mode = 'Delivery Mode';
			if(order && order.current_delivery_mode_new != ''){
				str_current_mode = order.current_delivery_mode_new ;
			}
			else{
				$('.delivery_mode').click();
			}
			return str_current_mode;
		},

		click_delivery_mode: function(){
			var self = this;
			if (self.gui.get_current_screen() != 'products'){
				return
				}
			self.select_delivery_mode({
				'security':     true,
				'current_mode': 'Dine-in',
				'title':      'Change Mode',
			})
		},


	});

	gui.define_popup({name:'delivery_mode', widget: DeliveryModeWidget});

	screens.ProductScreenWidget.include({
		show: function(reset){
			this._super();
			var order = this.pos.get_order();
			if(order.current_delivery_mode_new == ''){
				$('.delivery_mode').text('Delivery Mode')
				$('.delivery_mode').click();
			}
		},
	});

	chrome.OrderSelectorWidget.include({
		neworder_click_handler: function(){
			this._super();
		},

		renderElement: function(){
			var self = this;
			this._super();
			this.$('.order-button.select-order').off('click')
			this.$('.order-button.select-order').click(function(event){
				self.order_click_handler(event,$(this));
				var objOrder = self.pos.get_order();
				var obj_delivery_mode = self.pos.current_delivery_mode[[objOrder.pos_session_id,objOrder.sequence_number]]
				if (obj_delivery_mode && obj_delivery_mode.name){
					$('.delivery_mode').text(obj_delivery_mode.name);
				}
			});
		},

		get_order_by_uid: function(uid) {
			var orders = this.pos.get_order_list();
			for (var i = 0; i < orders.length; i++) {
				if (orders[i].uid === uid) {
					return orders[i];
				}
			}
			return undefined;
		},

		order_click_handler: function(event,$el) {
			var order = this.get_order_by_uid($el.data('uid'));
			if (order) {
				self.pos.set_order(order);
			}
		},

	});

	chrome.Chrome.include({
		build_widgets: function () {
			// add blackbox id widget to left of proxy widget
			var username_index = _.findIndex(this.widgets, function (widget) {
				return widget.name === "username";
			});

			this.widgets.splice(username_index, 0, {
				'name':   'delivery_mode',
				'widget': DeliveryModeWidget,
				'replace':  '.placeholder-DeliveryModeWidget',
			});
			this._super();
		},
	});

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({

		initialize: function(attr,options) {
			_super_order.initialize.apply(this,arguments);
			 this.current_delivery_mode_new = this.current_delivery_mode_new || "";
		},
		export_as_JSON: function() {
			var json = _super_order.export_as_JSON.apply(this,arguments);
			var str_delivery_mode_id = 1
			if (this.pos.current_delivery_mode[[this.pos_session_id,this.sequence_number]] && this.pos.current_delivery_mode[[this.pos_session_id,this.sequence_number]].id){
					var str_delivery_mode_id = this.pos.current_delivery_mode[[this.pos_session_id,this.sequence_number]].id
			}
			json.delivery_mode_id = str_delivery_mode_id;
			json.current_delivery_mode_new = this.current_delivery_mode_new;
			return json;
		},
		init_from_JSON: function(json){
			_super_order.init_from_JSON.apply(this,arguments);
			this.current_delivery_mode_new = json.current_delivery_mode_new;
		},


		set_delivery_mode :function(obj_delivery_mode){
			this.current_delivery_mode_new  = obj_delivery_mode.name
			this.trigger('change',this);
		},

		get_delivery_mode : function() {
			return this.current_delivery_mode_new
		},

		twentyfourhr_to_12hr_timeconversion:function(timeString){
			var H = +timeString.substr(0, 2);
			var h = (H % 12) || 12;
			var ampm = H < 12 ? " AM" : " PM";
			timeString = h + timeString.substr(2, 3) + ampm;
			return timeString;
		},
		
		get_order_line_by_id:function(line){
			var that = this;
			var rtn = {};
			$.each(that.get_orderlines(),function(index,orderline){
				if(orderline.id == line.line_id){
					rtn = orderline
					return false;
				}
			});
			return rtn;
		},

		getPrintData :function(){
			var asrChanges = {}
			var objOrder = this.pos.get_order()
			var obj_delivery_mode = this.pos.current_delivery_mode[[objOrder.pos_session_id,objOrder.sequence_number]]
			if (obj_delivery_mode && obj_delivery_mode.name){
				asrChanges['delivery_type'] = '--- ' + obj_delivery_mode.name + ' ---'
			}
			return asrChanges
		}
	});


	var DmPopupWidget = PosBaseWidget.extend({
		template: 'DmPopupWidget',
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},
		events: {
			'click .button.cancel':  'click_cancel',
			'click .btn-default':  'click_close',
			'click .img-responsive': 'click_confirm',
			'click .thumb-inner': 'click_item',
			'click .save-offer': 'click_save',
			'click .btn-primary-add-topping': 'click_topping',
			'click .topping-btn input[type="checkbox"]':  'click_items',
			'click .ddd':'qty_modify',
			'click .pizza-item' : 'prod_click',
		},

		// show the popup !
		show: function(options){
			if(this.$el){
				this.$el.removeClass('oe_hidden');
			}

			if (typeof options === 'string') {
				this.options = {title: options};
			} else {
				this.options = options || {};
			}

			this.renderElement();


		},

		// called before hide, when a popup is closed.
		// extend this if you want a custom action when the
		// popup is closed.
		close: function(){
			if (this.pos.barcode_reader) {
				this.pos.barcode_reader.restore_callbacks();
			}
		},
		qty_modify : function(){
		},

		hide: function(){
			if (this.$el) {
				this.$el.addClass('oe_hidden');
			}
		},
		click_close: function(){

		},
		click_topping: function(event){},

		click_items: function(event){},
		// what happens when we click cancel
		// ( it should close the popup and do nothing )
		click_cancel: function(){
			this.gui.close_popup();
			if (this.options.cancel) {
				this.options.cancel.call(this);
			}
		},

		// what happens when we confirm the action
		click_confirm: function(){
			this.gui.close_popup();
			if (this.options.confirm) {
				this.options.confirm.call(this);
			}
		},

		// Since Widget does not support extending the events declaration
		// we declared them all in the top class.
		click_item: function(){},
		click_numad: function(){},
		click_offer_item: function(){},
		click_save: function(){},
	});
	gui.define_popup({name:'alert', widget: DmPopupWidget});



	var DeliveryModeSelectionPopupWidget = DmPopupWidget.extend({
		template: 'DeliveryModeSelectionPopupWidget',
		show: function(options){
			options = options || {};
			var self = this;
			this._super(options);

			this.list    = options.list    || [];
			this.renderElement();

		},
		click_item : function(event) {
			this.gui.close_popup();
			if (this.options.confirm) {
				var item = this.list[parseInt($(event.target).data('item-index'))];
				item = item ? item.item : item;
				this.options.confirm.call(self,item);
			}
		}

	});
	gui.define_popup({name:'delivery_mode_selection', widget: DeliveryModeSelectionPopupWidget});


return {
	DeliveryModeWidget: DeliveryModeWidget,
	Model: Model,
	// deliveryModeWidgetBind : deliveryModeWidgetBind,
	DeliveryModeSelectionPopupWidget : DeliveryModeSelectionPopupWidget
};
});
