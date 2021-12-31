odoo.define('pos_network_printer.Multiprint', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var mixins = require('web.mixins');
    var Session = require('web.Session');

    var QWeb = core.qweb;
    var _t = core._t;

    models.Order = models.Order.extend({
        printChanges: function () {
            var self = this;

            function delay(ms) {
                var d = $.Deferred();
                setTimeout(function () {
                    d.resolve();
                }, ms);
                return d.promise();
            }
            var printers = this.pos.printers;
            for (var i = 0; i < printers.length; i++) {
                var changes = this.computeChanges(printers[i].config.product_categories_ids);
                changes.moment_date = moment().format('DD/MM/YYYY');
                changes.moment_time = moment().format('hh:mm a');
                if (changes['new'].length > 0 || changes['cancelled'].length > 0) {
                    _.each(changes.new, function (line) {
                        // quantity
                        var nb = String(line.qty);
                        if (nb.length == 1) {
                            line.qty_nb = '<pre>  ' + line.qty + '</pre>';
                        }
                        else if (nb.length == 2) {
                            line.qty_nb = '<pre> ' + line.qty + '</pre>';
                        }
                        else if (nb.length == 3) {
                            line.qty_nb = line.qty;
                        }
                        line.space_numb = '<pre>     ' + line.qty + ' x ' + line.name_wrapped[0] + '</pre>';
                    });
                    _.each(changes.cancelled, function (line) {
                        // quantity
                        var nb = String(line.qty);
                        if (nb.length == 1) {
                            line.qty_nb = '<pre>  -' + line.qty + '</pre>';
                        }
                        else if (nb.length == 2) {
                            line.qty_nb = '<pre> -' + line.qty + '</pre>';
                        }
                        else if (nb.length == 3) {
                            line.qty_nb = '-' + line.qty;
                        }
                        line.space_numb = '<pre>     ' + line.qty + ' x ' + line.name_wrapped[0] + '</pre>';
                    });
                    var receipt = QWeb.render('OrderChangeReceipt', {changes: changes, widget: self, printer:printers[i]});
                    if (self.pos.config.printing_mode == 'offline') {
                        printers[i].print(self, receipt);
                    }
                    if (self.pos.config.printing_mode == 'online') {
                        printers[i].print_online(self, receipt);
                    }
                    delay(100);
                }
            }
        },
    });

});