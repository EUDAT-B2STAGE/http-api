(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController);

function SearchController($scope, $log, $state, search)
{
    $log.info("Ready to search");

    function preProcessData(data) {

      var elements = [];
      forEach(data, function (x, i) {

// CHECK FOR DOCS images

        //console.log(x);
        elements.push({
// Checks on positions?
          'id': 
            x.record,
          'fête': 
            x.steps[2].data[0].value,
          'source': 
            x.steps[1].data[0].value,
          'extrait':
            x.steps[0].data[0].value,
        });
      });
        //console.log(elements);
      return elements;

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


/* LOADING BAR
    cfpLoadingBar.start();
    $timeout(function() {
        console.log("TEST completed timeout");
        cfpLoadingBar.complete();
    }, 400);
*/
    // INIT
    loadData();

}

})();