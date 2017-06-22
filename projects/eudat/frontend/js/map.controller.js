(function() {
  'use strict';

var app = angular.module('web').controller('MapController', MapController);

// The controller
function MapController($scope, $rootScope, $log, $timeout, noty, DataService, leafletMapEvents, leafletData)
{
	var self = this;

    // Docs:
    // http://angular-ui.github.io/ui-leaflet/#!/examples/events

    // Problem: tiles aren't loaded until window is resized/refreshed
    // Also reported here: https://github.com/tombatossals/angular-leaflet-directive/issues/49
    // Solution: force an invalidateSize after the page loading

    DataService.searchBoundingBox().then(
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
		    $scope.a = bounds._northEast.lat
		    $scope.b = bounds._northEast.lng
		    $scope.c = bounds._southWest.lat
		    $scope.d = bounds._southWest.lng
		});
    });

}


})();