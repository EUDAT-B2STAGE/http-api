(function() {
  'use strict';

///////////////////////////////////////////
///////////////////////////////////////////
/********************/
angular
    .module('web')
/********************/

//////////////////////////////
.controller('DataController', function($scope, $state) {
    console.log("TEST DATA")
})
//////////////////////////////
.controller('DataIDController', function($scope, $state, $stateParams) {
    $scope.id = $stateParams.id ;
})
//////////////////////////////
.service('auth', authService)
//////////////////////////////
.controller('MainController', MainController);



///////////////////////////////////////////
// https://thinkster.io/angularjs-jwt-auth
///////////////////////////////////////////
function authService($window, $http) {
  var self = this;
// Add JWT methods here

    self.saveToken = function(token) {
      $window.localStorage['jwtToken'] = token;
      return token;
    }
    self.getToken = function() {
      return $window.localStorage['jwtToken'];
    }

    self.login = function(token) {
        var req = {
            method: 'GET',
            url: 'http://awesome.dev:8081' + '/' + 'api/checklogged',
            headers: {
            "Authentication-Token" : token
            //   'Content-Type': undefined
            },
            //data: { test: 'test' }
        }

        return $http(req).then(
            function successCallback(response) {
                console.log("OK");
                console.log(response);
                return self.saveToken(token);
          }, function errorCallback(response) {
                console.log("FAILED TO LOG");
                console.log(response);
                return self.saveToken(null);
        });
    }


}

//////////////////////////////
function MainController($scope, $log, $location, auth) {
/*
    $log.debug("Controller");
    console.log($location);
    var absUrl = $location.absUrl();
    $log.debug($location.$$url);
*/

var token = "WyIxIiwiODFmMjFhNWVkMTA4MjY0ZDk1ZjJmZDFiZTlhZWVjMDYiXQ.CVgRvg.UQqt6SGH6Hd5nyPaLl1rNYOCCVw" // + "BB"

    auth.login(token).then(function logged(some){
        console.log("Token in storage is:", auth.getToken());
    });

    /////////////////////////////////////
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


  }
})();
