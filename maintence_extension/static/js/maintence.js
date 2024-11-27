odoo.define("maintence_extension.sign", function (require) {
  "use strict";

  const publicWidget = require("web.public.widget");
  console.log("LOADED SIGNATURE WIDGET");

  publicWidget.registry.MaintenceSign = publicWidget.Widget.extend({
    selector: "#containerprueba",
    events: {
      'click #clear-signature-btn': "_cleanSign",
      'click #sheet_submit_button': '_clickSaveButton',
      'click #submit_signature_button': '_clickFinalizeButton',
      'click #start_maintenance_button': '_clickStartMaintenanceButton',
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
      return this._super(...arguments);
    },

    _cleanSign: function (e) {
      this.$signaturePad.jSignature("reset");
    },

    _clickSaveButton: function (e) {
        const target = e.target;
        const maintence_id = target.getAttribute("maintence-id");

        let taskStates = [];
        $('input.form-check-input[type="checkbox"]').each(function() {
            let nameAttr = $(this).attr('name');
            if (nameAttr) {
                let taskId = nameAttr.split('_')[1];
                let taskState = $(this).is(':checked') ? 'realizado' : 'pendiente';
                taskStates.push({ id: taskId, state: taskState });
            } else {
                console.error("Checkbox without a name attribute found.");
            }
        });

        console.log("Task States:", taskStates);

        this._rpc({
            route: '/my/maintenance_order/update',
            params: {
                id: maintence_id,
                stage_id: $('select[name="stage_id"]').val(),
                duration: $('input[name="duration"]').val(),
                request_date: $('input[name="request_date"]').val(),
                observations: $('textarea[name="observations"]').val(),
                tasks: taskStates,
                action: 'save'
            },
        }).then(function (response) {
            window.location.reload();
        }).catch(function (error) {
            console.error("Error updating maintenance order:", error);
        });
    },

    _clickFinalizeButton: function (e) {
      console.log("CLICKED FINALIZE BUTTON");
      const maintence_id = $('#submit_signature_button').attr("maintence-id");
      let signatureData = this.$signaturePad.jSignature("getData", "image");

      this._rpc({
          route: '/my/maintenance_order/update',
          params: {
              id: maintence_id,
              signature: signatureData[1],
              action: 'finalize',
              observations: $('textarea[name="observations"]').val(),
          },
      }).then(function (response) {
          window.location.reload();
      }).catch(function (error) {
          console.error("Error finalizing maintenance order:", error);
      });
    },
    _clickStartMaintenanceButton: function (e) {
        console.log("CLICKED START MAINTENANCE BUTTON");
        const maintence_id = $('#start_maintenance_button').attr("maintence-id");

        this._rpc({
            route: '/my/maintenance_order/update_stage',
            params: {
                id: maintence_id,
            },
        }).then(function (response) {
            window.location.reload();
        }).catch(function (error) {
            console.error("Error starting maintenance order:", error);
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
