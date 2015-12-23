/*
(function() {
  'use strict';

angular.module('web')
.service('reqs', requestsService)
.controller('LoggedController', LoggedController)

//////////////////////////////
function LoggedController($scope, $log, reqs) {

    console.log("LOGGED");
}

//////////////////////////////
function requestsService($window, $http, $auth, $log) {

    var self = this;

    // Recover host/protocol info
    var host = $location.host();
    var protocol = $location.protocol();
    var apiPort = 8081;
    self.loginUrl = protocol + "://" + host + ":" + apiPort;

    self.authenticatedRequest = function() {

        var token = $auth.getToken();

        var req = {
            method: 'GET',
            url: self.loginUrl + '/checklogged',
            headers: { "Authentication-Token" : token },
        }

        return $http(req).then(
            function successCallback(response) {
                console.log("OK");
                console.log(response);
          }, function errorCallback(response) {
                $log.warn("Expired or invalid token! (REMOVE ME FROM COOKIE)");
                //console.log(response);
        });
    }
}

})();
*/