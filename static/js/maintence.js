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
        console.log("aqui")
        const target = e.target;
        const maintence_id = target.getAttribute("maintence-id");
        let signatureData = this.$signaturePad.jSignature("getData", "image");
        console.log("maintence_id", maintence_id);
        console.log("signatureData", signatureData);
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
