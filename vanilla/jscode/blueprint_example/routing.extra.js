(function() {
'use strict';

angular.module('web')
 .constant('blueprint_exampleRoutes',
 {
// JUST A TEST
    'test': {
        url: "/test",
        ///////////////////////////
        // This is mandatory for the configuration
        resolve: {
            skipAuhtenticationCheck: true,
            redirectIfNotAuthenticated: false,
        },
        ///////////////////////////
        views: {
            "main": {
                dir: 'custom',
                // OR
                //dir: 'base',
                templateUrl: 'test.html',
            }
        }
    },
///////////////
// LOGGED TEST
    'logged.test': {
        url: "/yes",
        resolve: {
            skipIfAuthenticated: false,
            redirectIfNotAuthenticated: true,
        },
        views: {
            "loggedview": {
                dir: 'custom',
                templateUrl: 'test.html',
            }
        }
    },
    'logged.test.sub': {
        url: "/:id",
        resolve: {
            skipIfAuthenticated: false,
            redirectIfNotAuthenticated: true,
        },
        views: {

// ADD SUBVIEW IN PARENT AND USE IT
            "sub": {
// OVERWRITING A PARENT VIEW
            //"loggedview@logged": {
                dir: 'custom',
                templateUrl: 'sub.html',
            }
        }
    }
///////////////
 });

})();