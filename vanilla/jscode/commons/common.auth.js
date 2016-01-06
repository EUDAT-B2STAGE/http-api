(function() {
  'use strict';

angular.module('web')
//.service('auth', authService)
.controller('LoginController', LoginController)
.controller('LogoutController', LogoutController)

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

/* NOTE TO SELF:
A quick note to make login/logout work in combination with flask:

JS works wherever you want, while python pages has to be really loaded
to make python code work on server side.

To make this possible you have to use buttons,
were you make the browser go to URLs which are not intercepted by angular router.

As i found out here:
http://stackoverflow.com/a/25799503
there is a quick paragraph in angular docs to make this happen:
https://docs.angularjs.org/guide/$location

"In cases like the following, links are not rewritten; 
instead, the browser will perform a full page reload to the original link.
Links that contain target element
Example: <a href="/ext/link?a=b" target="_self">link</a>
Absolute links that go to a different domain
Example: <a href="http://angularjs.org/">link</a>
Links starting with '/' that lead to a different base path
Example: <a href="/not-my-base/link">link</a>"

So for login i can make the page reload, for instance 
(do not like much for now)
While for logout i made the button "Yes" to let it happen. 


*/

//////////////////////////////
function LoginController($scope, $window, $location, $log, $auth, $state, $timeout) {

    $log.debug("Login Controller");
    $scope.load = true;
    $timeout(function() {
        var token = $auth.getToken();
        $log.debug("Actual token is:", token);
        if (token !== null) {
            $state.go('logged');
        } else {
            $scope.load = false;
        }
    }, 1200);

    $scope.loginfun = function(credentials) {
        $log.debug("Requested with", credentials);

        $auth.login(credentials).then(
            function (loginResponse) {
                console.log(loginResponse);
                console.log($auth.getToken());
/////////////////////////////////////////
// THERE IS NO WAY TO MAKE THIS TWO IN ONE COMMAND...
                //$state.go('logged');
                $window.location.reload();
/////////////////////////////////////////

            }, function(errorResponse) {
                $log.warn("Failed");
                console.log(errorResponse.data.errors);

            }
            );
    }
}

function LogoutController($scope, $log, $auth) 
{
    $log.debug("Logout Controller");

    $scope.logoutfun = function() {

        console.log("Logging out");
    	$auth.logout().then(function() {
            console.log("Token cleaned:", $auth.getToken());
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
