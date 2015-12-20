(function() {
  'use strict';

    angular.module('web').config(config);

    function config($logProvider, $locationProvider, $interpolateProvider,
        $stateProvider, $urlRouterProvider) {
    	// Enable log
    	$logProvider.debugEnabled(true); //.hashPrefix('!');
        // HTML5 mode: remove hash bang to let url be parsable
        $locationProvider.html5Mode(true);
        // Change angular variables from {{}} to [[]]
        $interpolateProvider.startSymbol('[[').endSymbol(']]');

        $stateProvider
            .state('home', {
                url: "/",
                views: {
                    "main": {
                        template: 'Home page<br>Go to <a ui-sref="data">link</a>.',
                        controller: 'MainController',
                    }
                },
            })

            ////////////////////////////
            .state("login", {
                url: "/login",
                 views: {
                    "main": {
                        templateUrl: '/static/app/templates/login.html',
                        controller: 'LoginController',
                    }
                }
            })
            .state("logged", {
                url: "/app",
                 views: {
                    "main": {
                        template: '<b>Logged</b>!!!',
                        controller: 'MainController',
                    }
                }
            })
            ////////////////////////////

            .state("data", {
            url: "/data",
                views: {
                    "main": {
                        template: 'Welcome to data page <div ui-view="id"></div>',
                        controller: 'DataController',

                    }
                }
                })
           .state("data.id", {
            url: "/:id",
                views: {
                    "id": {
                        template: '<h1>id = [[id]]</h1>',
                        controller: 'DataIDController',

                    }
                },


            });


        $urlRouterProvider.otherwise('/notfound');
    }


})();