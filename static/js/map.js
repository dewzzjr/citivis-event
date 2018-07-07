
function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: -7.2574719, lng: 112.7520883 },
        zoom: 13
    });

    if (locations.length < 4 && locations.length > 0) {
        var center = { lat: locations[0].lat, lng: locations[0].lng }
        map.panTo(center);
    }

    for (var i = 0; i < locations.length; i++) {
        var tmpLat = locations[i].lat;
        var tmpLng = locations[i].lng;
        var label = labels[i];

        var marker = _newGoogleMapsMarker({
            _map: map,
            _lat: tmpLat,
            _lng: tmpLng,
            _head: '|' + new google.maps.LatLng(tmpLat, tmpLng),
            _data: label
        });
    }
}

function _newGoogleMapsMarker(param) {
    var r = new google.maps.Marker({
        map: param._map,
        position: new google.maps.LatLng(param._lat, param._lng),
        title: param._head
    });
    if (param._data) {
        google.maps.event.addListener(r, 'click', function () {
            // this -> the marker on which the onclick event is being attached
            if (!this.getMap()._infoWindow) {
                this.getMap()._infoWindow = new google.maps.InfoWindow();
            }
            this.getMap()._infoWindow.close();
            this.getMap()._infoWindow.setContent(param._data);
            this.getMap()._infoWindow.open(this.getMap(), this);
        });
    }
    return r;
}

function setMarker(map) {
    var markers = [];
    var contentString = [];

    for (var i = 0; i < locations.length; i++) {
        var location = locations[i];
        var label = labels[i];

        markers[i] = new google.maps.Marker({
            position: location,
            map: map
        });

        contentString[i] = label;
        mark = markers[i];

        google.maps.event.addListener(
            mark, 'click', setBehaviour(
                mark, markers, contentString
            )
        );
    }

}

function setBehaviour(mark, markers, contentString) {
    if (mark.infowindow) {
        mark.infowindow.close();
    }

    mark.infowindow = new google.maps.InfoWindow({
        content: contentString[markers.indexOf(this)]
    });

    mark.infowindow.open(map, mark);
}
