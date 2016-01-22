(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single view on", $stateParams.id);

    function loadData() {

      // SINGLE DETAILS
      search.getSingleData($stateParams.id).then(function(out_single)
      {
          if (out_single.element < 1) {
            $scope.showSimpleToast("No data found for current id!");
            return false;
          }
          console.log("DETAILS1", out_single);
          // STEPS INFO
          search.getSteps().then(function(steps)
          {
              console.log("DETAILS2", steps);
              $scope.stepnames = steps;
              //$scope.data = out_single.data[0].steps;
          });
      });
    } // END FUNCTION

    loadData();
}

})();
