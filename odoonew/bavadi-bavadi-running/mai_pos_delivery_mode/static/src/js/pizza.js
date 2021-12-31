odoo.define('mai_pos_delivery_mode.pizza', function (require) {
"use strict";
	
	var Widget = require('web.Widget');
	var BaseWidget=require('point_of_sale.BaseWidget');
	var models = require('point_of_sale.models');
	var db = require('point_of_sale.DB');
	var screens = require('point_of_sale.screens');
	var PopupWidget=require('point_of_sale.popups');
	var gui = require('point_of_sale.gui');
	var core = require('web.core');
	var rpc = require('web.rpc');

	// var Model = require('web.DataModel');
	// var formats = require('web.formats');
	var utils = require('web.utils');
	var round_di = utils.round_decimals;
	var QWeb = core.qweb;
	var round_pr = utils.round_precision;
	var _t = core._t;

	var field_utils = require('web.field_utils');

	var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
	  "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"
	];

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({

		initialize: function() {
			_super_order.initialize.apply(this,arguments);
			this.is_delivery_available=this.is_delivery_available || false;
		},

		set_delivery_available:function(bool){
			this.is_delivery_available=bool;
		},

		export_as_JSON: function() {
			var json = _super_order.export_as_JSON.apply(this,arguments);
			json.is_delivery_available     = this.is_delivery_available;
			return json;
		},

		init_from_JSON: function(json) {
			_super_order.init_from_JSON.apply(this,arguments);
			this.is_delivery_available = json.is_delivery_available;
		},

		// Checks If Delivery Type product is added
		//Appends the new product to the last sequence
		add_product: function(product, options){
			if(this._printed){
				this.destroy();
				return this.pos.get_order().add_product(product, options);
			}
			if (product.pos_categ_id[1] == 'Delivery'){
				if (this.is_delivery_available != true){
				this.set_delivery_available(true);
				}
				else{
				 this.pos.gui.show_popup('delivery',{});
				return false;
				}
			}
			this.assert_editable();
			options = options || {};
			var attr = JSON.parse(JSON.stringify(product));
			attr.pos = this.pos;
			attr.order = this;
			var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});

			if(options.quantity !== undefined){
				line.set_quantity(options.quantity);
			}
			if(options.price !== undefined){
				line.set_unit_price(options.price);
			}
			if(options.discount !== undefined){
				line.set_discount(options.discount);
			}

			if(options.extras !== undefined){
				for (var prop in options.extras) {
					line[prop] = options.extras[prop];
				}
			}

			var last_orderline = this.get_last_orderline();
			if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false && line.product.is_offer == false ){
				last_orderline.merge(line);
			}else{
				this.orderlines.add(line);
			}
			this.select_orderline(this.get_last_orderline());
		},


	
		remove_orderline: function( line ){
			this.assert_editable();

			if (line.product.pos_categ_id[1] == 'Delivery'){
				this.set_delivery_available(false);
			}

			for(var len = 0, j = this.orderlines.models.length-1; j >= len; j--){
				if (line.id == this.orderlines.models[j].parent_orderline){
				this.orderlines.remove(this.orderlines.models[j]);
				}
			}

			this.orderlines.remove(line);
			this.select_orderline(this.get_last_orderline());
		},

	});

	

	screens.ReceiptScreenWidget.include({

		renderElement: function() {
			var self = this;
			var order = self.pos.get_order();
			this._super();
			
			//Fiscal Print Generation
			this.$('.button.print-custom').click(function(){
				if (!self._locked) {
					var orderlines=[];
					for(var i = 0, len = self.pos.get_order().orderlines.models.length; i < len; i++){
					orderlines.push({'product':self.pos.get_order().orderlines.models[i].product.display_name,'qty':self.pos.get_order().orderlines.models[i].quantity,
					'amount':round_pr(self.pos.get_order().orderlines.models[i].price*
					(1 - self.pos.get_order().orderlines.models[i].discount/100),self.pos.currency.rounding)
					})
					}
					var fiscal = Backbone.Collection.extend({
						url:'http://192.168.2.117/'
					});

					var fiscalobj=new fiscal();
					fiscalobj.url="http://localhost/perl/";
					var datas={'orderlines':orderlines,'partner':order.partner_id,'total':order.get_total_with_tax()+
					order.get_total_discount(),'total_paid':order.get_total_paid(),
					'delivery_mode':order.current_delivery_mode_new,'ordername':order.name};
					fiscalobj.fetch({
						dataType: 'json',
						type:'POST',
						data:{"data":orderlines},
						jsonpCallback:'success',
						success: function (e) {
							console.log(' Service request success: '+e);
							console.log(e);
						},
						error: function (e) {
						//console.log(' Service request failure: ' + e);
							console.log(' Service request failure: ' + e);
						},
						complete: function (e) {
							console.log(' Service request completed ');
						}
					});
					if(self.pos.get_order().current_delivery_mode_new !="Dine In"){
						self.print();
					}
				}
			});
		},


		get_receipt_render_env: function() {
	        var order = this.pos.get_order();
	        var creation_date=order.creation_date.toString();
			var month=creation_date.substring(4,7);
			var day=creation_date.substring(8,10);
			var year=creation_date.substring(13,15);
			var time=creation_date.substring(16,25);
	        return {
	          	widget:this,
				month:month,
				day:day,
				year:year,
				order: order,
				time:time,
				receipt: order.export_for_printing(),
				orderlines: order.get_orderlines(),
				paymentlines: order.get_paymentlines(),
	        };
	    },
	});

	

	var DuplicateDeliveryDialog = PopupWidget.extend({
		template:'DuplicateDeliveryDialog',

		events: {
			'click .ok':  'click_ok',
			},

		 show: function(options){
				this._super(options);
				},

		 click_ok:function(event){
			  this.gui.close_popup();
		 }

	});

	gui.define_popup({name:'delivery', widget: DuplicateDeliveryDialog});

	

	BaseWidget.include({
		format_currency_without_decimals:function(amount,precision){
			var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 0};
			amount = this.format_currency_no_symbol_no_decimal(amount,precision);
			if (currency.position === 'after') {
				return amount + ' ' + (currency.symbol || '');
			} else {
				return (currency.symbol || '') + ' ' + amount;
			}
		},
		format_currency_no_symbol_no_decimal: function(amount, precision) {
			var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 0};
			var decimals = 0;
			if (precision && this.pos.dp[precision] !== undefined) {
				decimals = this.pos.dp[precision];
			}

			if (typeof amount === 'number') {
				amount = round_di(amount,decimals).toFixed(decimals);
				amount = field_utils.format.float(round_di(amount, decimals), {digits: [69, decimals]});
			}
			return amount;
		},
	});

});

