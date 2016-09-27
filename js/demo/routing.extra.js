(function() {
'use strict';

angular.module('web').constant('customRoutes',
 {
// JUST A TEST
// Note: this will automatically check api online as not subchild of 'logged'
    'test': {
        url: "/test",
        views: {
            "main": {
                dir: 'blueprint',
                // OR
                //dir: 'base',
                templateUrl: 'test.html',
            }
        }
    },
///////////////
// LOGGED TEST
// Note: this will automatically check auth since is subchild of 'logged'
    'logged.test': {
        url: "/yes",
        views: {
            "loggedview": {
                dir: 'blueprint',
                templateUrl: 'test.html',
            }
        }
    },
    'logged.test.sub': {
        url: "/:id",
        views: {

// ADD SUBVIEW IN PARENT AND USE IT
            "sub": {
// OVERWRITING A PARENT VIEW
            //"loggedview@logged": {
                dir: 'blueprint',
                templateUrl: 'sub.html',
            }
        }
    }
///////////////
 });

})();
