odoo.define('pos_network_printer.Printer', function (require) {
    'use strict';
    var core = require('web.core');
    var rpc = require('web.rpc');
    var mixins = require('web.mixins');

    var Printer = core.Class.extend(mixins.PropertiesMixin, {
        init: function (parent) {
            mixins.PropertiesMixin.init.call(this, parent);
            this.receipt_queue = [];
        },
        print: function (widget, receipt) {
            var self = this;
            if (receipt) {
                this.receipt_queue.push(receipt);
            }

            function send_printing_job() {
                if (self.receipt_queue.length > 0) {
                    var receipt_xml = self.receipt_queue.shift();
                    var order = widget.pos.get_order();
                    var receipt_data = {
                        "uid": order.uid,
                        "printer_ip": self.config.proxy_ip,
                        "printer_port": self.config.printer_port,
                        "receipt": receipt_xml,
                    }

                    var receipt_db = widget.pos.db.load('receipt', []);
                    receipt_db.push(receipt_data);
                    widget.pos.db.save('receipt', receipt_db);

                    var json_data = {
                        "jsonrpc": "2.0",
                        "params": receipt_data,
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
                        data: JSON.stringify(json_data),
                        success: function (res) {
                            var data = JSON.parse(res.result);
                            if (data.error == 0) {
                                self.remove_printed_order_change(widget, data.uid);
                            }
                            if (data.error == 1) {
                                widget.pos.set({printer: {state: 'disconnected'}, spooler: {state: 'connecting'}});
                            }
                        }
                    });
                }
            }

            send_printing_job();
        },
        remove_printed_order_change: function (widget, uid) {
            var receipt = widget.pos.db.load('receipt', []);
            var printed_receipt = receipt.pop();
            if (printed_receipt.uid != uid) {
                receipt.push(printed_receipt);
            }
            widget.pos.db.save('receipt', receipt);
        },

        print_online: function (widget, receipt) {
            var self = this;
            if (receipt) {
                this.receipt_queue.push(receipt);
            }

            function send_printing_job() {
                if (self.receipt_queue.length > 0) {
                    var receipt_xml = self.receipt_queue.shift();
                    var queue_print_data = {
                        "printer_name": self.config.name,
                        "printer_ip": self.config.proxy_ip,
                        "printer_port": self.config.printer_port,
                        "connector_id": self.config.connector_id[0],
                        "receipt": receipt_xml,
                        "token": self.get_connector_token(widget, self.config),
                    }

                    rpc.query({
                        model: 'queue.print',
                        method: 'create',
                        args: [queue_print_data]
                    }).then(function (result) {
                        console.log('new queue created ' + 1);
                    });
                }
            }

            send_printing_job();
        },
        get_connector_token: function (widget, printer) {
            var connector = _.filter(widget.pos.printer_connectors, function (line) {
                return line.id == printer.connector_id[0]
            });
            return connector[0].token;
        }
    });
    return Printer;
});