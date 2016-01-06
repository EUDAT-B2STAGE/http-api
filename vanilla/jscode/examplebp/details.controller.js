(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single view on", $stateParams.id);

    function loadData() {

      // SINGLE DETAILS
      search.getSingleData($stateParams.id).then(function(out_single){
        if (checkApiResponseTypeError(out_single)) {
            setScopeError(out_single);
        } else {
            if (out_single.count < 1) {
               setScopeError("No data found");
               return;
            }
          // STEPS INFO
          search.getSteps().then(function(out_steps) {
            if (checkApiResponseTypeError(out_steps)) {
                setScopeError(out_steps);
            } else {
                var steps = [];
                forEach(out_steps.data, function (obj, i) {
                    steps[obj.step.num] = obj.step.name;
                });
                $scope.stepnames = steps;

                //DOCUMENTS
                search.getDocs($stateParams.id).then(function(out_docs) {
                  if (checkApiResponseTypeError(out_docs)) {
                    setScopeError(out_docs);
                  } else {
                      if (out_docs.count > 0) {
                          $scope.images = out_docs.data[0].images;
                          $log.debug("Found images", $scope.images);
                      } 
                      $scope.data = out_single.data[0].steps;
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
