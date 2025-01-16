odoo.define('maintenance_extension.openlayers_map', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.MaintenanceMap = publicWidget.Widget.extend({
        selector: '#map-container',

        start: function () {
            this._super(...arguments);
            this.initMap();
            this._bindResizeEvent();
        },

        initMap: function () {
            console.log("Initializing Map...");

            const spainCenter = ol.proj.fromLonLat([-3.7038, 40.4168]);

            this.map = new ol.Map({
                target: 'map-container',
                layers: [
                    new ol.layer.Tile({
                        source: new ol.source.OSM()
                    })
                ],
                view: new ol.View({
                    center: spainCenter,
                    zoom: 12
                })
            });

            this.markers = [];
            this.updateMarkers();

            this.map.on('click', this.handleMapClick.bind(this));
        },

        handleMapClick: function (event) {
            const clickedCoordinate = event.coordinate;
            const clickedLonLat = ol.proj.toLonLat(clickedCoordinate);

            console.log("Clic en el mapa en las coordenadas (Lon, Lat): ", clickedLonLat);

            let closestDistance = Infinity;
            let closestOrder = null;

            this.markers.forEach(order => {
                const markerCoordinate = order.coordinate;
                const markerLonLat = ol.proj.toLonLat(markerCoordinate);
                const distance = ol.sphere.getDistance(clickedLonLat, markerLonLat);

                console.log("Distancia del clic al marcador: ", distance);

                const thresholdDistance = 25;
                if (distance <= thresholdDistance && distance < closestDistance) {
                    closestDistance = distance;
                    closestOrder = order;
                }
            });

            if (closestOrder) {
                console.log("Clic cerca del marcador, redirigiendo...");
                const url = this.buildRedirectUrl(closestOrder.id, closestOrder.access_token);
                window.location.href = url;
            } else {
                console.log("No se hizo clic cerca de ningún marcador.");
            }
        },

        updateMarkers: function () {
            console.log("Updating Markers...");

            this.markers.forEach(marker => this.map.removeLayer(marker.layer));
            this.markers = [];

            let minLat = Infinity, maxLat = -Infinity, minLon = Infinity, maxLon = -Infinity;

            fetch('/maintenance/orders/locations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
                .then(response => response.json())
                .then(data => {
                    console.log("Data received:", data);

                    if (Array.isArray(data.result)) {
                        data.result.forEach(order => {
                            const latitude = this.roundCoordinate(order.latitude / 1000000);
                            const longitude = this.roundCoordinate(order.longitude / 1000000);

                            minLat = Math.min(minLat, latitude);
                            maxLat = Math.max(maxLat, latitude);
                            minLon = Math.min(minLon, longitude);
                            maxLon = Math.max(maxLon, longitude);

                            const markerColor = this.getMarkerColor(order.state);

                            const marker = new ol.Feature({
                                geometry: new ol.geom.Point(ol.proj.fromLonLat([longitude, latitude])),
                                name: order.name
                            });

                            marker.setStyle(new ol.style.Style({
                                image: new ol.style.Circle({
                                    radius: 10,
                                    fill: new ol.style.Fill({ color: markerColor }),
                                    stroke: new ol.style.Stroke({ color: '#fff', width: 2 })
                                })
                            }));

                            const vectorSource = new ol.source.Vector({
                                features: [marker]
                            });

                            const vectorLayer = new ol.layer.Vector({
                                source: vectorSource
                            });

                            this.map.addLayer(vectorLayer);

                            this.markers.push({
                                layer: vectorLayer,
                                coordinate: ol.proj.fromLonLat([longitude, latitude]),
                                id: order.id,
                                access_token: order.access_token
                            });
                        });

                        if (this.markers.length > 0) {
                            const extent = ol.extent.boundingExtent([
                                ol.proj.fromLonLat([minLon, minLat]),
                                ol.proj.fromLonLat([maxLon, maxLat])
                            ]);

                            const buffer = 0.2;
                            ol.extent.scaleFromCenter(extent, 1 + buffer);

                            this.map.getView().fit(extent, {
                                padding: [50, 50, 50, 50],
                                duration: 300,
                                maxZoom: 15
                            });
                        }
                    } else {
                        console.error('Unexpected data format:', data);
                    }
                })
                .catch(error => console.error('Error fetching locations:', error));
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

        roundCoordinate: function (value) {
            return Math.round(value * 1000000) / 1000000;
        },

        buildRedirectUrl: function (orderId, accessToken) {
            const currentUrl = new URL(window.location.href);
            const queryParams = new URLSearchParams(currentUrl.search);

            const redirectUrl = new URL(`/my/maintenance_order/${orderId}`, window.location.origin);
            redirectUrl.searchParams.set('access_token', accessToken);

            queryParams.forEach((value, key) => {
                redirectUrl.searchParams.set(key, value);
            });

            return redirectUrl.toString();
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
