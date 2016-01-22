(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController)
    .controller('ChipsController', ChipsController)
    .controller('TreeController', TreeController)
    .controller('AutoCompleteController', AutoCompleteController)
    ;

function SearchController($scope, $log, $state, search)
{

  // INIT controller
  var self = this;
  $log.debug("Main SEARCH controller");

  // Template Directories
  self.templateDir = templateDir;
  self.customTemplateDir = customTemplateDir;

  // INIT scope variables
  $scope.data = {};
  $scope.results = false;

  //TABS
  self.selectedTab = null;
  self.onTabSelected = function () {
      $log.debug("Selected", self.selectedTab);
  }


  $scope.ucFirst = function(string) {
    return string.capitalizeFirstLetter();
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
    $scope.dataCount = response.elements;
    $scope.results = true;

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

function ChipsController($scope, $log, search)
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
      $log.info("Requested tag:", chip, "total:", self.chips);

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
        self.dataCount = NaN;
        if (!out_data || out_data.elements < 1) {
          return null;
        }
        $scope.fillTable(out_data);
      });
  }

  self.removeChip = function(chip, index) {
// IF YOU REMOVE YOU SHOULD REBUILD THE QUERY FROM START...
// JUST USE THE SAME FUNCTION OF NEW CHIP
    //console.log(chip, index);
    $log.error("Not implemented. It should be soon!");
  }

}

////////////////////////////////
// controller
////////////////////////////////
function AutoCompleteController($scope, $log, $q, search)
{

  // Init controller
  var self = this;
  $log.debug("Auto Complete controller");

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
              if (api_response.elements > 1) {
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

////////////////////////////////
// controller
////////////////////////////////

function TreeController($scope, $log, search)
{
  // Init controller
  var self = this;
  $log.debug("Tree controller");

// https://github.com/wix/angular-tree-control

    // options are found http://wix.github.io/angular-tree-control/
    $scope.treeOptions = {
        nodeChildren: "children",
        dirSelectable: false, //true,
    /*
        isSelectable: function(node) {
          return node.label.indexOf("Joe") !== 0;
        },
    */
        injectClasses: {
            ul: "a1",
            li: "a2",
            liSelected: "a7",
            iExpanded: "a3",
            iCollapsed: "a4",
            iLeaf: "a5",
            label: "a6",
            labelSelected: "a8"
        }
    }
    $scope.showSelected = function(selected) {
      $log.info("Selected node", selected);
      $scope.selectedTreeObj = selected.info;
    };

  function treeProcessData(steps) {

    var tree = [];

    forEach(steps, function(single, i){
    var fields = [];
    forEach(single.fields, function(field, j){
      var infos = {
        'name': field.name,
        'values': field.options,
        'type': getType(field.type),
        'required': field.required,
      };
      fields.push({
        'type': 'field', 'name': field.name, 'info': infos,
        "children": []});
    });
    tree.push({
      'type': 'step', 'name': single.step.name,
      "children": fields});
    });

    $log.info("TREE", tree);
    $scope.myTree = tree;

  }

  ////////////////////////////////////////
  // move me into a service
  self.types = [
      {value: 0, text: 'string', desc:
          'All text is allowed'},
      {value: 1, text: 'number', desc:
          'Only integers values'},
      {value: 2, text: 'email', desc:
          'Only e-mail address (e.g. name@mailserver.org)'},
      {value: 3, text: 'url', desc:
          'Only web URL (e.g. http://website.com)'},
      {value: 4, text: 'date', desc:
          'Choose a day from a calendar'},
      {value: 5, text: 'time', desc:
          'Choose hour and minutes'},
      {value: 6, text: 'pattern', desc:
          'Define a regular expression for a custom type'},
      {value: 7, text: 'color', desc:
          'Only colors in hexadecimal value. Choose from color picker.'},
      {value: 8, text: 'list', desc:
          'Define a list of possible values (e.g. a dictionary)'},
  ];
  function getType(key) {
      // save type to be sure in the future?
      var type = self.types[0].text;
      if (self.types[key])
          type = self.types[key].text;
      return type;
  }
  ////////////////////////////////////////

}

})();