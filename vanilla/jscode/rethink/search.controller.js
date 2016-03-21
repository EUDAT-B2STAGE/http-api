(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController)
    .controller('ChipsController', ChipsController)
    ;

function SearchController($scope, $rootScope, $log, $state, search, hotkeys, keyshortcuts)
{

  // INIT controller
  var self = this;
  self.goToLastRoute = $rootScope.goToLastRoute;
  $log.debug("Main SEARCH controller");

    // Init keys
    hotkeys.bindTo($scope)
        .add({
            combo: "esc",
            description: "Quit from searching",
            callback: function() {
                keyshortcuts.exitSearch(event, self);
            }
        });

  // INIT scope variables
  $scope.data = {};
  $scope.dataCount = null;
  $scope.results = false;
  $scope.setDataCount = function (value) {
    $scope.results = true;
    $scope.dataCount = value;
  }

  //////////////////////////////////////////////////////////
  // https://material.angularjs.org/latest/demo/autocomplete

  function loadAll(data_steps) {

    // Prepare steps name
    var steps = [];
    forEach(data_steps, function(single, i){
      steps[single.step.num] = single.step.name;
    });
    $scope.stepsInfo = steps;

    // Prepare total array of autocomplete divided by types
    var auto = [];
    forEach($scope.autocomplete, function(data, step){
      forEach(data, function(state, key){
        auto.push({
          value: state.toLowerCase(),
          display: state,
          type: steps[step+1],
        })
      });
    });
    return auto;
  }

  $scope.fillTable = function(response)
  {
    $log.debug("FILLING TABLE");
    $scope.data = [];
    $scope.results = true;
    $scope.dataCount = response.elements;

    forEach(response.data, function (x, i)
    {
      // SINGLE DETAILS
      search.getSingleData(x.record, false)
       .then(function(element)
      {
          $scope.data.push(element);
// FIX HTML VIEW?
      });
    });
  }

  self.changePage = function(page) {
    $log.info("Page", page);
  }

}

////////////////////////////////
// controller
////////////////////////////////

function ChipsController($scope, $log, $q, $stateParams, search)
{

  // Init controller
  var self = this;
  $log.debug("Chip controller");

  // https://material.angularjs.org/latest/demo/chips
  self.chips = [];

  self.loadAllRecords = function () {
    $log.debug("Button to define");
// ACTION FOR ONLY THE BUTTON TO LOAD ALL ARCHIVE
    //search.getData().then(function(out_data){
  }

  self.newChip = function(chip) {
      $scope.setDataCount(null);
      $log.info("Requested tag:", chip, "total:", self.chips);
// TO FIX
// FOR EACH CHIPS
// ADD TO JSON TO MAKE MORE THAN ONE STEP ON RETHINKDB
// SO THIS WILL BE ONE SINGLE HTTP REQUEST
      // Choose table to query
      var promise = null;
      if (chip.type == 'Transcription') {
        promise = search.filterDocuments(chip.display);
      } else {
        promise = search.filterData(chip.display);
      }
      // Do query
      promise.then(function(out_data) {
        if (!out_data || out_data.elements < 1) {
          $scope.setDataCount(0);
          return null;
        }
        $scope.fillTable(out_data);
      });
  }

  self.removeChip = function(chip, index) {
// TO FIX
// IF YOU REMOVE YOU SHOULD REBUILD THE QUERY FROM START...
// JUST USE THE SAME FUNCTION OF NEW CHIP
    //console.log(chip, index);
    $log.error("Not implemented. It should be soon!");
  }

  // AUTOCOMPLETE CODE
  // HANDLE PARAMETER
  self.parameter = $stateParams.text;
  $log.debug("Auto Complete controller", self.parameter);

  if (self.parameter) {
    // Add value to chips
    var chip = {
        display: self.parameter,
        type: "Custom",
        value: self.parameter
    };
    self.chips.push(chip);
// TO FIX
    self.newChip(chip);
  }

  // Init scope
  self.searchText = null;
  self.states = [];

  // Functions to search with autocomplete
  function createFilterFor(query) {
    var lowercaseQuery = angular.lowercase(query);
    return function filterFn(state) {
      return (state.value.indexOf(lowercaseQuery) === 0);
    };
  }

  self.querySearch = function() {
    var query = self.searchText;
    $log.debug("Search", self.searchText)
    return query ?
        self.states.filter(createFilterFor(query)) :
        self.states;
  }

  self.searchAll = function () {
      $scope.setDataCount(null);
      // Do query
      search.getData().then(function(out_data) {
        if (!out_data || out_data.elements < 1) {
          return null;
        }
        $scope.fillTable(out_data);
      });
  }

////////////////////////////////////////
//http://solutionoptimist.com/2013/12/27/javascript-promise-chains-2/
  var
    initSearchComplete = function (argument) {
        return search.getSteps();
    },
    parallelLoad = function (steps) {

        console.log("STEPS", steps);
        if (steps.length < 1) {
           return false;
        }
        steps.push('Transcription')
// TO FIX
// should be a foreach on 'steps'
        var promises = {
            1: search.getDistinctValuesFromStep(1),
            2: search.getDistinctValuesFromStep(2),
            3: search.getDistinctValuesFromStep(3),
            4: search.getDistinctValuesFromStep(4),
            5: search.getDistinctTranscripts(),
        }
        return $q.all(promises).then((values) =>
        {
            forEach(values, function (api_response, step) {
              if (api_response.elements > 2) {
                $log.debug('Fullfilling step', steps[step]);
                //console.log(api_response);

                forEach(api_response.data, function(state, key){
                  self.states.push({
                    value: state.toLowerCase(),
                    display: state,
                        type: steps[step],
                  })
                });

              }
            });
            //throw( new Error("Just to prove catch() works! ") );
        });
    },
    reportProblems = function( fault )
    {
        $log.error( String(fault) );
    };

    initSearchComplete()
        .then( parallelLoad )
        .catch( reportProblems );

/* MIX STEPS AND AUTOCOMPLETE
    // Prepare total array of autocomplete divided by types
    var auto = [];
    forEach($scope.autocomplete, function(data, step){
      forEach(data, function(state, key){
        auto.push({
          value: state.toLowerCase(),
          display: state,
          type: steps[step+1],
        })
      });
    });
    return auto;
*/

    //self.states
// CHAINING PROMISES
////////////////////////////////////////

}

})();