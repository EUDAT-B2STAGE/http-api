(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single element");

    function preProcessData(data) {
        return data.steps;
    }

    function checkError(data) {
        return typeof data == 'string';
    }

    function error(message) {
       $log.error(message);
       $scope.error = "Service down...";
    }

    function loadData() {

      // SINGLE DETAILS
      search.getSingleData($stateParams.id).then(function(out_single){
        if (checkError(out_single)) {
            error(out_single);
        } else {
            if (out_single.count < 1) {
               $scope.error = "No data found";
               return;
            }
          // STEPS INFO
          search.getSteps().then(function(out_steps) {
            if (checkError(out_steps)) {
                error(out_steps);
            } else {
                var steps = [];
                forEach(out_steps.data, function (obj, i) {
                    steps[obj.step.num] = obj.step.name;
                });
                $scope.stepnames = steps;

                //DOCUMENTS
                search.getDocs($stateParams.id).then(function(out_docs) {
                  if (checkError(out_docs)) {
                    error(out_docs);
                  } else {
                      if (out_docs.count > 0) {
                          $scope.images = out_docs.data[0].images;
                          console.log("Found images", $scope.images);
                      } 
                      $scope.data = preProcessData(out_single.data[0]);
                  }
                });

            } // END IF
          });
        } // END IF
      });
    } // END FUNCTION

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
