(function() {
  'use strict';

angular.module('web')
    .controller('ExploreController', ExploreController)
    .controller('StepsController', StepsController)
    .controller('TreeController', TreeController)
    ;

function ExploreController($scope, $rootScope, $log, $state, search)
{

  // INIT controller
  var self = this;
  $log.debug("Explore data: controller");

  // INIT scope variables
  $scope.data = {};
  $scope.results = false;

  //TABS
  self.selectedTab = null;
  self.onTabSelected = function () {
      $log.debug("Selected", self.selectedTab);
      if (self.selectedTab == 1) {
          //Load data for the tree
          search.getSteps(true).then(function (out)
          {
            $rootScope.treeProcessData(out);
          })
      }
  }

  $scope.ucFirst = function(string) {
    return string.capitalizeFirstLetter();
  }

}

////////////////////////////////
// controller
////////////////////////////////

function StepsController($scope, $log, $state, search)
{
  // INIT controller
  $log.debug("Stepping in pieces");
  var self = this;
  self.step = 2;

  search.getDistinctValuesFromStep(self.step).then(function (out)
  {
        self.data = [];
        self.dataCount = self.data.length;
       if (out) {
           self.dataCount = out.elements;
           self.data = out.data;
       }
  })
}

////////////////////////////////
// controller
////////////////////////////////

function TreeController($scope, $rootScope, $log, search)
{
  // INIT controller
  $log.debug("Tree of life");
  var self = this;

  // Init scope data
  //self.dataCount = NaN;
  self.data = [];

// https://github.com/wix/angular-tree-control

    // options are found http://wix.github.io/angular-tree-control/
    self.treeOptions = {
        nodeChildren: "children",
        dirSelectable: false, //true,
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
    self.showSelected = function(selected) {
      $log.info("Selected node", selected);
      self.selectedTreeObj = selected.info;
    };

  $rootScope.treeProcessData = function (steps)
  {
    var tree = [];
    self.dataCount = steps.length;

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
    self.myTree = tree;

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