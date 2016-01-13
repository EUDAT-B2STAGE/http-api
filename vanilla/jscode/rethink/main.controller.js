(function() {
  'use strict';

///////////////////////////////////////////
///////////////////////////////////////////
/********************/
angular
    .module('web')
    .controller('FabButtonController', FabController)
    .controller('MainController', MainController);

//https://material.angularjs.org/latest/demo/fabSpeedDial
function FabController($scope, $log, $timeout)
{
    var self = this;
    $log.info("Fab");

    self.isOpen = false;
    self.tooltipVisible = false;
    self.availableModes = ['md-fling', 'md-scale'];
    self.selectedMode = 'md-scale';
    self.hover = false;

    self.items = [
        { name: "Twitter", icon: "twitter", direction: "bottom" },
        { name: "Facebook", icon: "facebook", direction: "top" },
        { name: "Google Hangout", icon: "hangout", direction: "bottom" }
    ];

      // On opening, add a delayed property which shows tooltips after the speed dial has opened
      // so that they have the proper position; if closing, immediately hide the tooltips
      $scope.$watch('demo.isOpen', function(isOpen) {
        if (isOpen) {
          $timeout(function() {
            $scope.tooltipVisible = self.isOpen;
          }, 600);
        } else {
          $scope.tooltipVisible = self.isOpen;
        }
      });
}

function MainController($scope, $log, $location, $timeout, cfpLoadingBar)
{
    $log.info("Main");

/*
    cfpLoadingBar.start();
    console.log("TEST before timeout");
    $timeout(function() {
        console.log("TEST completed timeout");
        $scope.some = "Hello world";
        cfpLoadingBar.complete();
    }, 2000);

    $scope.active = false;
    $scope.variab = 'testing';
    $scope.route = {
        "angular": false,
        //"id": 42,
        "new": false,
        "uhm": false,
    }

    var refresh = function() {

        $scope.active = false;

        // Recover current route from URL
        var paths = $location.$$url.substring(1).split('/');
        $log.debug(paths);

        // Expected routes
        var expected = Object.keys($scope.route);
        for (var i = 0; i < expected.length; i++) {
            $scope.route[expected[i]] = false;
        };

        for (var i = 0; i < paths.length; i++) {

            // One piece of the url at the time
            var current_url = paths[i];
            // No more routes
            if (current_url.trim() == "")
                break;
            // What we were expecting
            var current_route = expected[i];
            var current_val = $scope.route[current_route];

            // Check current state
            $log.debug("Check: ", current_url, "VS", current_route);
            if (current_url != current_route)
                break;
            $log.info(current_url, "expected");
            $scope.route[current_route] = true;

        };

        $log.warn("Result:", $scope.route)
        $scope.active = true;

        // // FIRST LEVEL
        // if ($scope.first) {
        //   $log.info("First");
        // }
        // // SECOND LEVEL
        // if ($scope.second) {
        //   $log.info("Second");
        // }
    }

    $scope.stepdown = function() {
        $log.info("Stepping down");
        var url = '';
        var expected = Object.keys($scope.route);
        for (var i = 0; i < expected.length; i++) {
            if(!$scope.route[expected[i+1]])
                break;
            var key = expected[i];
            url += '/' + key;
        };
        $location.$$url = url;
        $log.info("DOWN TO ", $location.$$url);
        refresh([]);
    }

    $scope.stepup = function() {
        $log.info("Stepping up");
        var url = '';
        var expected = Object.keys($scope.route);
        for (var i = 0; i < expected.length; i++) {
            var key = expected[i];
            url += '/' + key;
            if(!$scope.route[key])
                break;
        };
        $location.$$url = url;
        //$log.info($location.$$url);
        refresh([]);
    }

    refresh([]);

*/

}

})();