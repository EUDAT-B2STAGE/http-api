(function() {
'use strict';

angular.module('web')
 .constant('rethinkRoutes',

// EXTRA ROUTES
    {
        'logged.submit': {
            url: "/submit",
            resolve: {
                skipAuhtenticationCheck: false,
                redirectIfNotAuthenticated: true,
            },
            views: {
                "loggedview": {
                    dir: 'base',
                    templateUrl: 'home.html',
                }
            },
        }
    }

 ); // END CONSTANT

})();
