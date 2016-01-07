(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController);

function SearchController($scope, $log, $state, search)
{
  $log.info("Ready to search");
  var self = this;

  // Template Directories
  var framework = 'materialize';
  var templateDirBase = '/static/app/templates/';
  //var templateDir = templateDirBase + framework + '/';
  $scope.customTemplateDir = templateDirBase + 'custom/' + framework + '/';

////////////////////////////////////////
////////////////////////////////////////
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
////////////////////////////////////////

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

$scope.ucFirst = function(string) {
  return string.capitalizeFirstLetter();
}

function treeProcessData(steps) {

  var tree = [];

  forEach(steps, function(single, i){
    //console.log(i, single);
    var fields = [];
    forEach(single.fields, function(field, j){
      //console.log(field);
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
    //console.log(fields);
    tree.push({
      'type': 'step', 'name': single.step.name, 
      "children": fields});
  });

  console.log("TREE", tree);
  $scope.myTree = tree;

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
      $log.debug("Loading data");

      // Load autocomplete for each step
      $scope.autocomplete = [];
      for (var i = 0; i < 3; i++) {
        var json = {
          'limit': 0, 
          'autocomplete': {'step': i+1, 'position': 1}
        };
        search.getFromQuery(json).then(function(out_data) {
          if (out_data.count < 2) {
            return false;
          }
          $scope.autocomplete.push(out_data.data, i);
          console.log(out_data);
        });
      };

      // Load real data and filter

/*  RDB QUERY or FILTER
      var json = {'test': 'me'};
      search.getFromQuery(json).then(function(out_data) {
*/
      search.getData().then(function(out_data){
        console.log(out_data);
        if (checkApiResponseTypeError(out_data)) {
          setScopeError(out_data, $log, $scope);
        } else {
          search.getSteps().then(function(out_steps) { 
            treeProcessData(out_steps.data);
            return true;
            $scope.data = preProcessData(out_data.data);
            forEach($scope.data, function(x,i) {
              search.getDocs(x.id).then(function(out_docs) { 
                if (out_docs.count > 0) {

                  $scope.data[i].image = 
                    out_docs.data[0].images[0].filename.replace(/\.[^/.]+$/, "")
                      + '/TileGroup0/0-0-0.jpg';
                }
              }); // GET DOCUMENTS
            }); // FOREACH
          }); // STEPS
        } // ELSE
      }); // GET DATA
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