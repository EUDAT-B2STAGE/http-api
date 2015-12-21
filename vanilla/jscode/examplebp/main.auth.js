(function() {
  'use strict';
angular.module('web').service('auth', authService)
.controller('LoginController', LoginController)


.config(function($authProvider) {

        var host = $location.host();
        var protocol = $location.protocol();

	$authProvider.loginUrl = protocol + "://" + host + "/auth"; 
	$authProvider.tokenName = 'authentication_token';

	$authProvider.oauth1({
		  name: null,
		  url: null,
		  authorizationEndpoint: null,
		  redirectUri: null,
		  type: null,
		  popupOptions: null
	});

});
//////////////////////////////
function LoginController($scope, $log, $auth) {

    $log.debug("Login Controller");

/*
    var token = "WyIxIiwiODFmMjFhNWVkMTA4MjY0ZDk1ZjJmZDFiZTlhZWVjMDYiXQ.CVgRvg.UQqt6SGH6Hd5nyPaLl1rNYOCCVw" // + "BB"

    auth.authenticatedRequest(token)
     .then(function logged(some){
        console.log("Token in storage is:", auth.getToken());
    });
*/

    $scope.loginfun = function(credentials) {
        $log.debug("Requested with", credentials);

    	$auth.login(credentials).then(function (loginResponse) {
		console.log(loginResponse);
		console.log($auth.getToken());
        });
    }

}

///////////////////////////////////////////
// https://thinkster.io/angularjs-jwt-auth
///////////////////////////////////////////
function authService($window, $http, $log) {

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

        return $http(req).then(
            function successCallback(response) {
                $log.info("Authentication successful");
                return self.saveToken(response.data.user.authentication_token);
          }, function errorCallback(response) {
                $log.error("Authentication FAILED")
                //console.log(response);
                return self.saveToken(null);
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
          }, function errorCallback(response) {
                $log.warn("Expired or invalid token");
                //console.log(response);
                return self.saveToken(null);
        });
    }
}

})();
