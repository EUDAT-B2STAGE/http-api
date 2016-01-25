(function() {
  'use strict';

angular.module('web')
    .controller('ExploreController', ExploreController)
    .controller('TreeController', TreeController)
    ;

function ExploreController($scope, $log, $state, search)
{

  // INIT controller
  var self = this;
  $log.debug("Explore data: controller");

  // Template Directories
  self.templateDir = templateDir;
  self.customTemplateDir = customTemplateDir;
  self.blueprintTemplateDir = blueprintTemplateDir;

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