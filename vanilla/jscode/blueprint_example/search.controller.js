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
      elements.push({
        'id': x.record,
        'image': null,
// TO FIX: 
// Checks on positions?
// there must better options to get those values with the right names
        'fête': x.steps[2].data[0].value,
        'source': x.steps[1].data[0].value,
        'extrait': x.steps[0].data[0].value,
      });
    });
    return elements;
  }

  function loadData() {

      var json = {'test': 'me'};
      //search.getData().then(function(out_data){
      search.getFromQuery(json).then(function(out_data) {
        console.log(out_data);
        if (checkApiResponseTypeError(out_data)) {
          setScopeError(out_data, $log, $scope);
        } else {
          $scope.data = preProcessData(out_data.data);
          forEach($scope.data, function(x,i) {
            search.getDocs(x.id).then(function(out_docs) { 
              if (out_docs.count > 0) {

                $scope.data[i].image = 
                  out_docs.data[0].images[0].filename.replace(/\.[^/.]+$/, "")
                    + '/TileGroup0/0-0-0.jpg';
              }
            });
          });
        }
      });
  }

  $scope.search = function(input) {
    $log.info("Search!", input);
  }

  $scope.changePage = function(page) {
    $log.info("Page", page);
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