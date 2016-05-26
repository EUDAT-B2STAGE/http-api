(function() {
  'use strict';

angular.module('web')
//.service('auth', authService)
.controller('LoginController', LoginController)
.controller('RegisterController', RegisterController)
.controller('LogoutController', LogoutController)

.config(function($authProvider) {

	$authProvider.loginUrl = serverUrl + "/auth";
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
(even if I do not like much this, but that's the best for now)
While for logout i made the button "Yes" to let it happen.

*/

//////////////////////////////
function LoginController($scope, $log, $window,
    $auth, $mdToast, $document, $timeout, $state, noty)
{

    // Init controller
    $log.debug("Login Controller");
    var self = this;
    self.userMessage = null;

    // Init the models
    self.user = {
       username: null,
       password: null,
    };

    // In case i am already logged, skip
    if ($auth.isAuthenticated())
    {
        $timeout(function () {
            $log.warn("Already logged");
            $state.go('logged');
        });
    }

    // LOGIN LOGIC
    self.check = function() {

        var credentials = self.user;
        $log.debug("Requested with", credentials);

        $auth.login(credentials).then(
            function (loginResponse) {
                self.userMessage = null;
                $log.info("Login request", loginResponse);
                //console.log($auth.getToken());
                //$rootScope.logged = true;

                // Now we can check again reloading this page
                $window.location.reload();
                console.log("DO YOU SEE ME?")
                noty.showAll(loginResponse.data.errors, noty.WARNING);

            }, function(errorResponse) {

                $log.warn("Auth: failed", errorResponse);
                noty.showAll(errorResponse.data.errors, noty.ERROR);

                // self.userMessage = null;
                // var errors = errorResponse.data.errors;
                // $log.warn("Auth: failed", errors);
                // var key = Object.keys(errors)[0];
                // if (key == "Email requires confirmation.") {
                //     self.userMessage = key;
                // }
                // $scope.showSimpleToast(errors);


            }
        );
    }
}

function RegisterController($scope, $log, $auth, api)
{
    // Init controller
    var self = this;
    self.errors = null;
    self.userMessage = null;
    $log.debug("Register Controller");

    // In case i am already logged, skip
    if ($auth.isAuthenticated())
    {
        $timeout(function () {
            $log.warn("Already logged");
            $state.go('logged');
        });
    }

    // Init the models
    self.user = {
       email: null,
       name: null,
       surname: null,
       password: null,
       password_confirm: null,
    };

    self.request = function()
    {
        var credentials = self.user;
        if (credentials.name == null || credentials.surname == null)
            return false;

        $log.debug("Requested registration:", credentials);

        api.apiCall(api.endpoints.register, 'POST', credentials, null, true)
         .then(
            function(response) {
                $log.debug("REG Success call", response);

                if (response.status > 210) {
                    var errors = response.data.errors;
                    $log.warn("Registration: failed", errors);
                    self.errors = errors;
                    //$scope.showSimpleToast(errors);
                    $scope.showSimpleToast({'Invalid':'Failed to register...'});
                } else {
                    $scope.showSimpleToast({'Well done':'New user created'});
                    self.errors = null;
                    self.userMessage =
                        "Account registered. Pending admin approval.";
                }
            }
        );

    }
}


function LogoutController($scope, $rootScope, $log, $auth, $window, $state, api, noty)
{
    // Init controller
    $log.debug("Logout Controller");
    var self = this;

    // Log out satellizer
    self.exit = function() {

        // I am going to call log out on the python frontend
        api.apiCall(
            api.endpoints.logout, 'GET',
            undefined, undefined, true)
         .then(
          function(response) {
            $log.info("Logging out", response);

            console.log("LOGOUT IS ON PROGRESS AT THE MOMENT");
/*
        	$auth.logout().then(function() {
                $log.debug("Token cleaned:", $auth.getToken());
            });
            $window.location.reload();
            $rootScope.logged = false;
            //$state.go('welcome');
*/
          }, function(error) {
            $log.warn("Error for logout", error);
            noty.showAll([error.data], noty.ERROR);
          }
        );

    }

}

// THE END
})();