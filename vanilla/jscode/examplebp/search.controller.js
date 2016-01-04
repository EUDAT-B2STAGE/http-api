(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController);

function SearchController($scope, $log, $timeout, cfpLoadingBar, search)
{
    $log.info("Ready to search");
    cfpLoadingBar.start();

    $timeout(function() {
        console.log("TEST completed timeout");
        search.getData().then(function(out){
            if (typeof out == 'string') {
               $log.error(out);
               $scope.error = "Service down...";
            } else {
               console.log(out);
               $scope.data = out.data;
            }
        });
        cfpLoadingBar.complete();
    }, 400);
}

})();