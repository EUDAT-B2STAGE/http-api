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

/*****************************/

//REMOVEME
$scope.data = {}
//REMOVEME

  // https://material.angularjs.org/latest/demo/chips
  $scope.newChip = function(chip) {
    $log.info("Requested tag:", chip);
    if (typeof chip == 'string') {
      $log.debug("User chip");
      return {value:chip, display:chip, type:'custom'};
    }
  }

  // https://material.angularjs.org/latest/demo/autocomplete
  var self = this;
  self.states = loadAll();
  $scope.results = [];

  function loadAll() {
    var allStates = 'test, hello mah, hello world';
      return allStates.split(/, +/g).map( function (state) {
        return {
          value: state.toLowerCase(),
          display: state
        };
      });
  }
  function createFilterFor(query) {
    var lowercaseQuery = angular.lowercase(query);
    return function filterFn(state) {
      return (state.value.indexOf(lowercaseQuery) === 0);
    };
  }
  $scope.querySearch = function(query) {
    //$log.debug("CHECK", self.states);
    return query ? self.states.filter( createFilterFor(query) ) : self.states;
  }
/*
  $scope.searchTextChange = function(text) {
    $log.debug('Text changed to ' + text);
  }
*/
  $scope.selectedItemChange = function(item) {
    $log.info('Item changed to ' + JSON.stringify(item));
  }
/*****************************/

  function loadData() {

  return true;

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