(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single element");
    $scope.record = $stateParams.id;

    function preProcessData(data) {
        console.log(data);
        return data[0].steps;
    }

    function loadData() {

        search.getSingleData($stateParams.id).then(function(out){
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
