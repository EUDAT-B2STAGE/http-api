(function() {
  'use strict';

var app = angular.module('web').controller('MapController', MapController);

// The controller
function MapController($scope, $rootScope, $log, $timeout, noty, DataService, leafletMapEvents, leafletData)
{
	var self = this;
    self.NE_lat = 0;
    self.NE_lng = 0;
    self.SW_lat = 0;
    self.SW_lng = 0; 

    self.search_fields = [
        {
          key: 'min_date',
          type: 'datepicker',
          templateOptions: {
            type: 'date',
            required: true,
            label: 'Min date',
            placeholder: 'Select date'
          }
        },
        {
          key: 'max_date',
          type: 'datepicker',
          templateOptions: {
            type: 'date',
            required: true,
            label: 'Max date',
            placeholder: 'Select date'
          }
        },
    ]

    // Docs:
    // http://angular-ui.github.io/ui-leaflet/#!/examples/events

    // Problem: tiles aren't loaded until window is resized/refreshed
    // Also reported here: https://github.com/tombatossals/angular-leaflet-directive/issues/49
    // Solution: force an invalidateSize after the page loading

    self.search = function() {
        if (!self.search_form.$valid) return false;

        var min_date = self.search_model['min_date'];
        var max_date = self.search_model['max_date'];

        if (typeof min_date  === 'undefined') {
            noty.showError("Missing starting date");
            return;
        } 
        if (typeof max_date  === 'undefined') {
            noty.showError("Missing ending date");
            return;
        }

        console.log(self.SW_lng);

        DataService.searchBoundingBox(
                min_date, max_date, self.NE_lat, self.NE_lng, self.SW_lat, self.SW_lng
            ).then(
            function(out_data) {
                var data = out_data.data[1];

                self.data = data
                
                for (var i=0; i<data.length; i++) {
                    var marker = data[i]
                    $scope.markers[i] = {
                        lat: marker[2],
                        lng: marker[3],
                        message: marker[1],
                        focus: false,
                        draggable: false
                    }
                }
                console.log($scope.markers);

                noty.extractErrors(out_data, noty.WARNING);
            }, function(out_data) {

                noty.extractErrors(out_data, noty.ERROR);
            });
    };

    leafletData.getMap("mymap").then(function(map) {
      $timeout(function() {
        console.log("Map tiles refreshed");
        map.invalidateSize();
      }, 1000);
    });

    angular.extend($scope, {
        defaults: {
            scrollWheelZoom: true
        },
        events: {
            map: {
                enable: ['moveend'],
                logic: 'emit'
            }
        },
        markers: {
            // Rome: {
            //     lat: 41.9,
            //     lng: 12.45,
            //     message: "This is Rome!",
            //     focus: false,
            //     draggable: false
            // },
            // Bologna: {
            //     lat: 44.5,
            //     lng: 11.35,
            //     message: "This is Bologna!",
            //     focus: false,
            //     draggable: false
            // }
        }
    });


    $scope.center  = {
        lat: 41.9,
        lng: 12.45,
        zoom: 5
    };

    $scope.$on('leafletDirectiveMap.mymap.moveend', function(event){
		leafletData.getMap().then(function(map) {
		    var bounds = map.getBounds();
		    self.NE_lat = bounds._northEast.lat;
		    self.NE_lng = bounds._northEast.lng;
		    self.SW_lat = bounds._southWest.lat;
		    self.SW_lng = bounds._southWest.lng;
		});
    });

}


})();