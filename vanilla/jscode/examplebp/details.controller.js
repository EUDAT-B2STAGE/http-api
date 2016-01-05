(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single element");

    function preProcessData(data) {
        //console.log("Pre data", data);
        return data.steps;
    }

    function loadData() {

        search.getSingleData($stateParams.id).then(function(out_single){
            if (typeof out == 'string') {
               $log.error(out);
               $scope.error = "Service down...";
            } else {
               search.getSteps().then(function(out_steps) {
                    if (typeof out == 'string') {
                       $log.error(out);
                       $scope.error = "Service down...";
                    } else {
                        var steps = [];
                        forEach(out_steps.data, function (obj, i) {
                            steps[obj.step.num] = obj.step.name;
                        });
                        $scope.data = preProcessData(out_single.data[0]);
                        $scope.stepnames = steps;
                    }
               });
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
