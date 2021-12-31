odoo.define('pos_network_printer.NetworkDevices', function (require) {
    "use strict";
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var NetworkDevices = PosBaseWidget.extend({
        print_network_xmlreceipt: function (widget, receipt, printer) {
            var self = this;
            var order = widget.pos.get_order();
            var receipt_data = {
                "uid": order.uid,
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "receipt": receipt,
            }

            var receipt_db = widget.pos.db.load('receipt', []);
            receipt_db.push(receipt_data)
            widget.pos.db.save('receipt', receipt_db);

            var data = {
                "jsonrpc": "2.0",
                "params": receipt_data
            }
            $.ajax({
                dataType: 'json',
                headers: {
                    "content-type": "application/json",
                    "cache-control": "no-cache",
                },
                url: '/print-network-xmlreceipt',
                type: 'POST',
                proccessData: false,
                data: JSON.stringify(data),
                success: function (res) {
                    var data = JSON.parse(res.result);
                    if (data.error == 0) {
                        self.remove_printed_order(widget, data.uid);
                    }
                    if (data.error == 1) {
                        widget.pos.set({printer: {state: 'disconnected'}, spooler: {state: 'connecting'}});
                    }
                }
            });
        },

        remove_printed_order: function (widget, uid) {
            var receipt_db = widget.pos.db.load('receipt', []);
            var printed_receipt = receipt_db.pop();
            if (printed_receipt.uid != uid) {
                receipt_db.push(printed_receipt);
            }
            widget.pos.db.save('receipt', receipt_db);
        },

        print_network_xmlreceipt_online: function (widget, receipt, printer) {
            var self = this;
            var order = widget.pos.get_order();
            var queue_print_data = {
                // "uid": order.uid,
                "printer_name": printer.printer_name,
                "printer_ip": printer.printer_ip,
                "printer_port": printer.printer_port,
                "connector_id": printer.connector_id[0],
                "receipt": receipt,
                "token": self.get_connector_token(widget, printer),
            }
            rpc.query({
                model: 'queue.print',
                method: 'create',
                args: [queue_print_data]
            }).then(function (result) {
                console.log('new queue created ' + 1);
            });

        },
        get_connector_token: function (widget, printer) {
            var connector = _.filter(widget.pos.printer_connectors, function (line) {
                return line.id == printer.connector_id[0]
            });
            return connector[0].token;
        }

    });
    return NetworkDevices
});