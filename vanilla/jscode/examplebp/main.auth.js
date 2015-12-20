(function() {
  'use strict';
angular.module('web').service('auth', authService);

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

})();
