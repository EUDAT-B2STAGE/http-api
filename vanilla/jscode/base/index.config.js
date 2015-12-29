(function() {
  'use strict';

angular.module('web').config(config);

// Ui Resolve + Satellizer to authenticate
// source http://j.mp/1VnxlQS
function _skipIfAuthenticated($q, $state, $auth) {
    var defer = $q.defer();
    if($auth.isAuthenticated()) {
        defer.reject();
    } else {
        defer.resolve();
    }
    return defer.promise;
}
 
function _redirectIfNotAuthenticated($q, $state, $auth, $timeout) {
    var defer = $q.defer();
    if($auth.isAuthenticated()) {
        defer.resolve();
    } else {
        //console.log("TEST");
        $timeout(function () {
            //console.log("TEST2");
            $state.go('login');
        }); //, 100);
        defer.reject();
    }
    return defer.promise;
}

// ROUTES
function config($stateProvider, $urlRouterProvider, $authProvider, $logProvider, $locationProvider) //, $interpolateProvider)
{

	// Enable log
	$logProvider.debugEnabled(true); //.hashPrefix('!');
    // HTML5 mode: remove hash bang to let url be parsable
    $locationProvider.html5Mode(true);
    // Change angular variables from {{}} to [[]]
    //$interpolateProvider.startSymbol('[[').endSymbol(']]');

$stateProvider
    ////////////////////////////
    .state("login", {
        url: "/login",
        resolve: {
            skipIfAuthenticated: _skipIfAuthenticated
        },
        views: {
            "main": {
                //template: '<br><h1>test</h1> [[angular]]',
                templateUrl: '/static/app/templates/login.html',
                controller: 'LoginController',
            }
        }
    })
    .state("logout", {
        url: "/logout",
        views: {
            "main": {
                templateUrl: '/static/app/templates/logout.html',
                controller: 'LoginController',
            }
        }
    })
    .state("logged", {
        url: "/app",
        resolve: {
            redirectIfNotAuthenticated: _redirectIfNotAuthenticated
            //logginer: function($auth) {
        },
        // Abstract state?
        views: {
            "main": {
                template: "<div ui-view='loggedview'></div>",
                //controller: 'MainController',
            }
        },
    })

    .state('logged.search', {
        url: "/search",
        views: {
            "loggedview": {
                templateUrl: '/static/app/templates/home.html',
                controller: 'MainController',
            }
        },
    })

    //$urlRouterProvider.otherwise('/login');
    //$urlRouterProvider.otherwise('/app/search');

// Ui router kinda bug fixing 
// CHECK THIS IN THE NEAR FUTURE
//https://github.com/angular-ui/ui-router/issues/1022#issuecomment-50628789
    $urlRouterProvider.otherwise(function ($injector) {
        var $state = $injector.get('$state');
        //return $state.go('login');
        $state.go('login');
    });

}


})();