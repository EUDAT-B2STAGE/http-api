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
function LoginController($scope, $log, $window, $auth, $mdToast, $document, $timeout, $state)
{

    // Init controller
    $log.debug("Login Controller");
    var self = this;

    // Init the models
    self.user = {
       username: null,
       password: null,
    };

    // In case i am already logged, skip
    if ($auth.isAuthenticated()) {
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
                $log.info("Login request", loginResponse);
                //console.log($auth.getToken());

                // Now we can check again reloading this page
                $window.location.reload();

            }, function(errorResponse) {
                $log.warn("Auth: failed");
                console.log(errorResponse.data.errors);
                $scope.showSimpleToast(errorResponse.data.errors);
            }
        );
    }
}

function LogoutController($scope, $log, $auth)
{
    // Init controller
    $log.debug("Logout Controller");
    var self = this;

    // Log out satellizer
    self.exit = function() {
        $log.info("Logging out");
// TO FIX:
    // missing log out from APIs too
    	$auth.logout().then(function() {
            $log.debug("Token cleaned:", $auth.getToken());
        });
    }

}

// THE END
})();