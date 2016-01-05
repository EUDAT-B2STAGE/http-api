(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single element");
    $scope.record = $stateParams.id;

    function preProcessData(data) {
        return "One";
    }

    function loadData() {

        search.getData().then(function(out){
            if (typeof out == 'string') {
               $log.error(out);
               $scope.error = "Service down...";
            } else {
               $scope.data = preProcessData(out.data);
            }
        });
    }

    loadData();

/* LOADING BAR
    cfpLoadingBar.start();

    $timeout(function() {
        console.log("TEST completed timeout");
        cfpLoadingBar.complete();
    }, 400);
*/

}

})();
