var map;

function geocodeAddress(geocoder, resultsMap, event) {

    geocoder.geocode({'address': event.venue.address}, function(results, status) {

    if (status === 'OK') {
        //resultsMap.setCenter(results[0].geometry.location);
        var marker = new google.maps.Marker({
                                            map: resultsMap,
                                            position: results[0].geometry.location
                                            });

        contentString = '';
        for (var i = 0; i < event.events.length; i++) {

            contentString += '<div>'
            + '<b>Date : </b>' + event.events[i].event.date + '<br/>'
            + '<b>Artist : </b><a href="/showArtist/' +event.events[i].artist.id +'">' + event.events[i].artist.name + '</a>'
            + '</div><br/>' ;
        }

        var infowindow = new google.maps.InfoWindow({
          content: contentString
        });

        marker.addListener('click', function() {
          infowindow.open(resultsMap, marker);
        });


    } else {
        alert('Geocode was not successful for the following reason: ' + status);
    }
    });
}

function displayEvents(map, events) {
    console.log(events);
    var geocoder = new google.maps.Geocoder();
    for (var i = 0; i < events.length; i++) {
        geocodeAddress(geocoder, map, events[i])
    }
}

function populateMap(map) {

    var request = new XMLHttpRequest();
    request.open('POST', '/getEvents', true);

    request.onload = function() {
      if (request.status >= 200 && request.status < 400) {
        // Success!
        var resp = request.responseText;
        var values = JSON.parse(resp)

        var venues = values.venues;
        var events = values.events;
        var artists = values.artists;
        var allGrouped = [];
        var current;
        for (var i = 0; i < venues.length; i++) {
            current = {'venue': venues[i], 'events': []};
            for (var j = 0; j < events.length; j++) {
                if (venues[i].id == events[j].venue_id) {
                    for (var k = 0; k < artists.length; k++) {
                        if (events[j].band_id == artists[k].id) {
                            current.events.push({ 'artist' : artists[k], 'event' : events[j] });
                        }
                    }
                }
            }

            allGrouped.push(current);
        }
        displayEvents(map, allGrouped);
      } else {
        // We reached our target server, but it returned an error

      }
    };

    request.onerror = function() {
      // There was a connection error of some sort
      console.log("Error happened")
    };

    request.send();
}

function initMap() {

    var dublin = {lat: 53.350140, lng: -6.266155 };

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: dublin
    });

    populateMap(map);
}
