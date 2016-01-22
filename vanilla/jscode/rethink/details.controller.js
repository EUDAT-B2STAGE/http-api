(function() {
  'use strict';

angular.module('web')
    .controller('DetailsController', DetailsController);

function DetailsController($scope, $log, $stateParams, search)
{
    $log.info("Single view on", $stateParams.id);
    var self = this;
    self.data = null;

    function loadData() {

      // STEPS INFO
      search.getSteps().then(function(steps)
      {
        // This call is needed inside Search Service
        // at least once for Controller

        $scope.stepnames = steps;

        // SINGLE DETAILS
        search.getSingleData($stateParams.id, true)
         .then(function(out_single)
        {
            if (! out_single)
            {
              $scope.showSimpleToast("No data found for current id!");
              return false;
            }

            // Set data
            self.data = angular.copy(out_single);
            delete out_single.id;
            delete out_single.thumb;
            delete out_single.images;
            self.refinedData = out_single;

        }); // single data
      }); // steps
    } // END loadData FUNCTION

    // Use it
    loadData();
}

})();
