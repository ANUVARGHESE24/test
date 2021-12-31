odoo.define('odoo_debranding.user_menu', function (require) {
    "use strict";

    var core = require('web.core');

    var Usermenu = require('web.UserMenu')
    console.log("usermenu is: ", Usermenu)

    var _t = core._t;

    Usermenu.include({
         _onMenuAccount: function () {
               window.open('https://www.febno.com', '_blank');
         }
    });

});
