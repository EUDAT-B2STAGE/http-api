(function() {
  'use strict';
angular.module('web').service('auth', authService)
.controller('LoginController', LoginController)
;

//////////////////////////////
function LoginController($scope, $log, auth) {

    $log.debug("Login Controller");

/*
    var token = "WyIxIiwiODFmMjFhNWVkMTA4MjY0ZDk1ZjJmZDFiZTlhZWVjMDYiXQ.CVgRvg.UQqt6SGH6Hd5nyPaLl1rNYOCCVw" // + "BB"

    auth.authenticatedRequest(token)
     .then(function logged(some){
        console.log("Token in storage is:", auth.getToken());
    });
*/

    $scope.loginfun = function(some) {
        $log.debug("TEST", some);
        auth.requestToken(some);
    }

}

///////////////////////////////////////////
// https://thinkster.io/angularjs-jwt-auth
///////////////////////////////////////////
function authService($window, $http) {

    var self = this;
    var FE_URL = 'http://awesome.dev'
    var API_URL = 'http://awesome.dev:8081/api'

////////////
    self.saveToken = function(token) {
      $window.localStorage['jwtToken'] = token;
      return token;
    }
    self.getToken = function() {
      return $window.localStorage['jwtToken'];
    }
////////////

    self.requestToken = function(content) {
        var req = {
            method: 'POST',
            url: FE_URL + '/auth',
            // headers: {
            //   'Content-Type': undefined
            // },
            data: { 'username': content.email, 'password': content.pwd }
        }

        $http(req).then(
            function successCallback(response) {
                console.log("OK");
                console.log(response);
          }, function errorCallback(response) {
                console.log("FAILED");
                console.log(response);
        });
    }

    self.authenticatedRequest = function(token) {
        var req = {
            method: 'GET',
            url: API_URL + '/checklogged',
            headers: { "Authentication-Token" : token },
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

})();
