(function() {
  'use strict';

angular.module('web')
//.service('auth', authService)
.controller('LoginController', LoginController)

.config(function($authProvider) {

	$authProvider.loginUrl =
        window.location.protocol + "//"
        + window.location.host
        + "/auth";
	$authProvider.tokenName = 'authentication_token';

	$authProvider.oauth1({
		  name: null,
		  url: null,
		  authorizationEndpoint: null,
		  redirectUri: null,
		  type: null,
		  popupOptions: null
	});

})
;

//////////////////////////////
function LoginController($scope, $window, $log, $auth) {

    $log.debug("Login Controller");
    $log.debug("Actual token is:", $auth.getToken());

    $scope.loginfun = function(credentials) {
        $log.debug("Requested with", credentials);

        $auth.login(credentials).then(function (loginResponse) {
            console.log(loginResponse);
            console.log($auth.getToken());
            // Reload python pages
            $window.location.reload();
        });
    }

    $scope.logoutfun = function() {

        console.log("Logging out");
    	$auth.logout().then(function() {
    		console.log("TEST");
            //$window.location.reload();
            console.log($auth.getToken());
        });
    }

    // auth.authenticatedRequest(token)
    //  .then(function logged(some){
    //     console.log("Token in storage is:", auth.getToken());
    // });

}

// THE END
})();

/*
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
}
*/
