odoo.define('pos_product_view_app.screens', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var core = require('web.core');
var rpc = require('web.rpc');
var utils = require('web.utils');
var field_utils = require('web.field_utils');
var PopupWidget = require('point_of_sale.popups');
var QWeb = core.qweb;
var _t = core._t;

    var _super_posmodel = models.PosModel.prototype;      
      models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
          
            this.is_list = false;
          _super_posmodel.initialize.apply(this, arguments);
        },
     });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options) {
            _super_order.initialize.call(this,attr,options);
            this.is_list = this.is_list || "";
        },
        set_is_list: function(is_list){
            this.is_list = is_list;
            this.trigger('change',this);
        },
        get_is_list: function(is_list){
            return this.is_list;
        },        
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.call(this);
            json.is_list = this.is_list;
            return json;
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.is_list = json.is_list;
        },       
    });

    screens.ProductCategoriesWidget.include({
        init: function(parent, options){
            this._super(parent, options);         
        },       
        renderElement: function()
        {            
            var self = this;
            this._super();
            var order=self.pos.get_order()
            $('.js-product-list-view').click(function() {
                self.pos.is_list = true;
                order.set_is_list(true);
            });
            $('.js-product-grid-view').click(function() {                 
                self.pos.is_list = false;
                order.set_is_list(false);
            });
        },
    });

    screens.ProductListWidget.include({

        render_product: function(product){
            var current_pricelist = this._get_active_pricelist();
            var cache_key = this.calculate_cache_key(product, current_pricelist);
            var cached = false;
            if(!cached){
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{ 
                        widget:  this, 
                        product: product,
                        pricelist: current_pricelist,
                        image_url: this.get_product_image_url(product),
                    });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(cache_key,product_node);
                return product_node;
            }
            return cached;
        },
        render_products: function(product){
            var current_pricelist = this._get_active_pricelist();
            var cache_key = this.calculate_cache_key(product, current_pricelist);
            var cached = false;
            if(!cached){
                var product_html = QWeb.render('ProductListLine',{
                    widget:  this,
                    product: product,
                    pricelist: current_pricelist,
                    image_url: this.get_product_image_url(product),
                });
                var product_node = document.createElement('tbody');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(cache_key,product_node);
                return product_node;
            }
            return cached;
        },
        renderElement: function() {
            var el_str  = QWeb.render(this.template, {widget: this});
            var el_node = document.createElement('div');                
                el_node.innerHTML = el_str;
                el_node = el_node.childNodes[1];
            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;
            $(".product-tree").hide()
            if(!this.pos.is_list)
            {   
                $(".product-tree").hide();
                $(".product-grid").show();
                var list_container = el_node.querySelector('.product-list');                
                for(var i = 0, len = this.product_list.length; i < len; i++)
                {
                    var product_node = this.render_product(this.product_list[i]);
                    product_node.addEventListener('click',this.click_product_handler);
                    product_node.addEventListener('keypress',this.keypress_product_handler);
                    list_container.appendChild(product_node);
                }               
            }
            else
            {
                $(".product-grid").hide();
                $(".product-tree").show();
                            
                var list_container = el_node.querySelector('.product-list-contents');
                for(var i = 0, len = this.product_list.length; i < len; i++)
                {
                    var product_node = this.render_products(this.product_list[i]);                    
                    product_node.addEventListener('click',this.click_product_handler);
                    product_node.addEventListener('keypress',this.keypress_product_handler);
                    list_container.appendChild(product_node);
                }        
            }   
        },
    });

});