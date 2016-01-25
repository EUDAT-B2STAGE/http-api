(function() {
'use strict';

angular.module('web')
 .constant('rethinkRoutes',

// EXTRA ROUTES
    {

    //////////////////////
/*
        'logged.submit': {
            url: "/submit",
            // resolve: {
            //     skipAuhtenticationCheck: false,
            //     redirectIfNotAuthenticated: true,
            // },
            views: {
                "loggedview": {
                    dir: 'base',
                    templateUrl: 'home.html',
                }
            },
        },
*/

    //////////////////////
        'logged.specialsearch': {
            url: "/search/:text",
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'search.html',
                }
            },
        },

    //////////////////////
        'logged.explore': {
            url: "/explore",
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'explore.html',
                }
            },
        },

    //////////////////////
        'logged.details': {
            url: "/details/:id",
            views: {
                "loggedview": {
                    dir: 'blueprint',
                    templateUrl: 'details.html',
                }
            }
        },

    //////////////////////

    }

 ); // END CONSTANT

})();
