(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController);

function SearchController($scope, $log, $state, $mdConstant, search)
{
  $log.info("Ready to search");
  var self = this;
  $scope.data = {};

  // Template Directories
  // var framework = 'materialize';
  // var templateDirBase = '/static/app/templates/';
  // $scope.templateDir = templateDirBase + framework + '/';
  // $scope.customTemplateDir = templateDirBase + 'custom/' + framework + '/';
  $scope.templateDir = templateDir;
  $scope.customTemplateDir = customTemplateDir;

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

  function reloadTable(response) {

    var elements = [];
    if (!$scope.stepsInfo) {
      return {};
    }
    $log.debug("preprocess");
    $scope.data = [];

    forEach(response.data, function (x, i) {

      //console.log("DATA", x);

      // SINGLE DETAILS
      search.getSingleData(x.record).then(function(out_single){

        //$log.debug("Single element", x.record);
        if (checkApiResponseTypeError(out_single)) {
          setScopeError(out_single, $log, $scope);
        } else {
          if (out_single.count < 1) {
             setScopeError("No data found", $log, $scope);
             return;
          }
        }
        //console.log("SINGLE", out_single);
        var element = {
          'id': x.record,
          'image': null,
          // 'fête': null, //x.steps[2].data[0].value,
          // 'source': null, //x.steps[1].data[0].value,
          // 'extrait': null, //x.steps[0].data[0].value,
        }

        // skip last step, skip 0 which is not defined
        for (var l = $scope.stepsInfo.length - 2; l > 0; l--) {
            element[$scope.stepsInfo[l].toLowerCase()] = null;
        };

/////////////////
//BAD
// THIS IS VERY LOW IN PERFORMANCE
// I SHOULD GET THIS FROM THE QUERY IN ITSELF
        forEach(out_single.data[0].steps, function(y, j){
          var key = $scope.stepsInfo[y.step].toLowerCase();
          var value = null;
          for (var j = 0; j < y.data.length; j++) {
            if (y.data[j].position == 1) {
              element[key] = y.data[j].value;
              break;
            }
            //console.log("Position", j, y);
          };
        });
//BAD
/////////////////

        search.getDocs(x.record).then(function(out_docs) {
          if (out_docs.count > 0) {
            element.image =
              out_docs.data[0].images[0].filename.replace(/\.[^/.]+$/, "")
                + '/TileGroup0/0-0-0.jpg';
          }

          // FINALLY ADD DATA
          $scope.data.push(element);
          $scope.dataCount = response.count;
        }); // GET DOCUMENTS
      });
    });
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

  //////////////////////////////////////////////////////////
  // https://material.angularjs.org/latest/demo/autocomplete
  self.states = {};

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
/*
    var allStates = 'test, hello mah, Hello world';
      return allStates.split(/, +/g).map( function (state) {
        return {
          value: state.toLowerCase(),
          display: state
        };
      });
*/
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
  $scope.selectedItemChange = function(item) {
    $log.info('Item changed to ' + JSON.stringify(item));
  }
*/
/*****************************/

  function loadData() {
    $log.debug("Loading data");

    ///////////////////////////////////
    // Load autocomplete for each step
    $scope.autocomplete = [];
    $scope.dataCount = NaN;
    var steps = 3;
    for (var i = 0; i < steps; i++) {
      var json = {
        'limit': 0,
        'autocomplete': {'step': i+1, 'position': 1}
      };
      search.getFromQuery(json).then(function(out_data) {
        // Check only on first call
        if (checkApiResponseTypeError(out_data)) {
          // Set error and break
          setScopeError(out_data, $log, $scope);
          $scope.data = null;
          return false;
        } else if (out_data.count < 2) {
          return false;
        }
        $scope.autocomplete.push(out_data.data);
        // if ($scope.autocomplete.length == steps) {
        //   self.states = loadAll();
        // }
      });
      if ($scope.data === null){
        return false;
      }
    };

    ///////////////////////////////////
    // Load real data and filter

    // Get all
    search.getData().then(function(out_data){
        if ($scope.data === null) {
          return false;
        }
        // Get steps info
        search.getSteps().then(function(out_steps) {
          // Autocomplete setup from steps also
          self.states = loadAll(out_steps.data);
          // Create the table
          reloadTable(out_data);

          // Make the tree
          treeProcessData(out_steps.data);

        }); // STEPS
    }); // GET DATA

  }

  // https://material.angularjs.org/latest/demo/chips

  $scope.chips = [];

  $scope.newChip = function(chip) {

/* INSTRUCTIONS
one of the following return values:

an object representing the $chip input string
undefined to simply add the $chip input string, or
null to prevent the chip from being appended
*/
      $log.info("Requested tag:", chip, "total:", $scope.chips);
      var json = {
        //'limit': 0,
        'nested_filter': {'position': 1, 'filter': chip.display}
      };
      search.getFromQuery(json).then(function(out_data) {
        $scope.dataCount = NaN;
        // Check only on first call
        if (checkApiResponseTypeError(out_data)) {
          // Set error and break
          setScopeError(out_data, $log, $scope);
          $scope.data = null;
          return false;
        }
        if (out_data.count < 1) {
          return false;
        }
        reloadTable(out_data);
        //console.log(out_data);
      });
  }

  $scope.removeChip = function(chip, index) {

    //console.log("Delete chip, total:", $scope.chips);
    //console.log(chip, index);
    search.getData().then(function(out_data){
        if ($scope.data === null) {
          return false;
        }
        // Get steps info
        search.getSteps().then(function(out_steps) {
          // Create the table
          reloadTable(out_data);
        }); // STEPS
    }); // GET DATA
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