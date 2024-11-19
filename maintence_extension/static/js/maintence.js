odoo.define("maintence_extension.sign", function (require) {
  "use strict";

  const publicWidget = require("web.public.widget");
  console.log("LOADED SIGNATURE WIDGET");

  publicWidget.registry.MaintenceSign = publicWidget.Widget.extend({
    selector: "#form_maintence",
    events: {
      'click #clear-signature-btn': "_cleanSign",
      'click #sheet_submit_button': '_clickSaveButton',
    },

    init: function () {
      this._super(...arguments);
      console.log("TechnicalFormSign widget initialized");
      this.$signaturePad = $("#signature-pad").empty().jSignature({
        "decor-color": "#D1D0CE",
        "background-color": "rgba(255,255,255,0)",
        "show-stroke": false,
        color: "#000000",
        lineWidth: 2,
        width: 300,
        height: 100,
      });
      this.divCicked = false;
      this.divMouseOvered = false;
    },

    start: function () {
      console.log("TechnicalFormSign widget started");
      console.log(
        "signaturePad",
        this.$signaturePad,
        "divCicked",
        this.divCicked,
        "divMouseOvered",
        this.divMouseOvered
      );
      // this.checkSignInValuesBeforeSubmit();
      // this.checkIfDivWasClicked();
      // this.checkifDivWasMouseOvered();
      return this._super(...arguments);
    },

    _cleanSign: function (e) {
      this.$signaturePad.jSignature("reset");
      // $("#signature-data").val("");
      // $("#signature-error").hide();
    },

   _clickSaveButton: function (e) {
        console.log("aqui");
        const target = e.target;
        const maintence_id = target.getAttribute("maintence-id");
        let signatureData = this.$signaturePad.jSignature("getData", "image");
        console.log("maintence_id", maintence_id);
        console.log("signatureData", signatureData);

        let taskStates = [];
        $('input.form-check-input[type="checkbox"]').each(function() {
            let taskId = $(this).attr('name').split('_')[1];
            let taskState = $(this).is(':checked') ? 'realizado' : 'pendiente';
            taskStates.push({ id: taskId, state: taskState });
        });

        this._rpc({
            route: '/my/maintenance_order/update',
            params: {
                id: maintence_id,
                stage_id: $('select[name="stage_id"]').val(),
                duration: $('input[name="duration"]').val(),
                request_date: $('input[name="request_date"]').val(),
                work_done: $('textarea[name="work_done"]').val(),
                materials_used: $('textarea[name="materials_used"]').val(),
                observations: $('textarea[name="observations"]').val(),
                signature: signatureData[1],
                tasks: taskStates
            },
        }).then(function (response) {
            window.location.href = '/my/maintenance_orders';
        }).catch(function (error) {
            console.error("Error updating maintenance order:", error);
        });
    },

    checkIfDivWasClicked: function (e) {
      let div = document.getElementById("signature-pad");
      div.onclick = function () {
        this.divCicked = true;
        console.log("DIV WAS CLICKED", this.divCicked);
      };
    },

    checkifDivWasMouseOvered: function (e) {
      let div = document.getElementById("signature-pad");
      div.onmouseover = function () {
        this.divMouseOvered = true;
        console.log("DIV WAS MOUSE OVERED", this.divMouseOvered);
      };
    },
  });
});
