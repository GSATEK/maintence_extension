odoo.define('maintenance_extension.single_order_map', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.SingleOrderMap = publicWidget.Widget.extend({
        selector: '#single-order-map-container',

        start: function () {
            this._super(...arguments);
            this.initMap();
            this._bindResizeEvent();
        },

        initMap: function () {
            console.log("Initializing Single Order Map...");
            this.map = new ol.Map({
                target: 'single-order-map-container',
                layers: [
                    new ol.layer.Tile({
                        source: new ol.source.OSM()
                    })
                ],
                view: new ol.View({
                    center: ol.proj.fromLonLat([0, 0]),
                    zoom: 2
                })
            });

            this.updateMarker();
        },

        updateMarker: function () {
            console.log("Updating Marker...");
            const orderId = this.$el.data('order-id');
            console.log("Order ID:", orderId);

            fetch(`/maintenance/order/location/${orderId}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Data received:", data);

                    if (data.result) {
                        const latitude = this.roundCoordinate(data.result.latitude / 1000000);
                        const longitude = this.roundCoordinate(data.result.longitude / 1000000);

                        console.log("Latitude:", latitude, "Longitude:", longitude);

                        const markerColor = this.getMarkerColor(data.result.state);
                        this.addMarker(latitude, longitude, markerColor);
                        this.map.getView().setCenter(ol.proj.fromLonLat([longitude, latitude]));
                        this.map.getView().setZoom(15);

                        console.log("Marker added");
                    } else {
                        console.error('Unexpected data format:', data);
                    }
                })
                .catch(error => console.error('Error fetching location:', error));
        },

        getMarkerColor: function (state) {
            switch (state) {
                case 'Nueva solicitud':
                    return 'blue';
                case 'En progreso':
                    return 'green';
                case 'Pendiente de firma cliente':
                    return 'yellow';
                default:
                    return 'red';
            }
        },

        addMarker: function (latitude, longitude, color) {
            const marker = new ol.Overlay({
                position: ol.proj.fromLonLat([longitude, latitude]),
                positioning: 'center-center',
                element: this.createMarkerElement(color),
                stopEvent: false
            });

            this.map.addOverlay(marker);
            marker.setPosition(ol.proj.fromLonLat([longitude, latitude]));
        },

        createMarkerElement: function (color) {
            const element = document.createElement('div');
            element.style.backgroundColor = color;
            element.style.width = '20px';
            element.style.height = '20px';
            element.style.borderRadius = '50%';
            element.style.position = 'absolute';
            return element;
        },

        roundCoordinate: function (value) {
            return Math.round(value * 1000000) / 1000000;
        },

        _bindResizeEvent: function () {
            window.addEventListener('resize', () => {
                if (this.map) {
                    this.map.updateSize();
                }
            });
        }
    });
});