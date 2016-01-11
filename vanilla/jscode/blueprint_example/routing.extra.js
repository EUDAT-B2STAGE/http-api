(function() {
'use strict';

angular.module('web')
 .constant('rethinkRoutes',
 {
// JUST A TEST
    'test': {
        url: "/test",
        resolve: {
            skipIfAuthenticated: true,
        },
        views: {
            "main": {
                dir: 'base',
                //dir: 'custom',
                templateUrl: 'test.html',
            }
        }
    }
///////////////
 });

/*
myApp.provider('unicornLauncher', function UnicornLauncherProvider() {
  var useTinfoilShielding = false;

  this.useTinfoilShielding = function(value) {
    useTinfoilShielding = !!value;
  };

  this.$get = function unicornLauncherFactory(apiToken) {

    // let's assume that the UnicornLauncher constructor was also changed to
    // accept and use the useTinfoilShielding argument
    return new UnicornLauncher(apiToken, useTinfoilShielding);
  };
});
*/

/*
angular.module('web')
    .config(myconfig);

// Note: change name 'myconfig' to avoid same name in same space
function myconfig(
	$logProvider, $locationProvider, $interpolateProvider,
    $stateProvider, $urlRouterProvider
 ) {
    $stateProvider
        .state('logged.somestate', {
            url: "/someurl",
            views: {
                "loggedview": {
                    template: 'Home page<br>Go to <a ui-sref="data">link</a>.',
                    //controller: 'SomeController',
                }
            },
        })
}
*/

})();