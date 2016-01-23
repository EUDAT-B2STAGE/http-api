(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController);

function SearchController($scope, $rootScope, $log, $state, search)
{
  // Init
  $log.info("Ready to search");
  //$rootScope.avoidTheToolbar = true;
  var self = this;

  // Template Directories
  self.templateDir = templateDir;
  self.customTemplateDir = customTemplateDir;
  self.blueprintTemplateDir = blueprintTemplateDir;

  $scope.data = {};
  $scope.chips = [];

// https://material.angularjs.org/latest/demo/chips
  $scope.newChip = function(chip) {

/* INSTRUCTIONS
one of the following return values:

an object representing the $chip input string
undefined to simply add the $chip input string, or
null to prevent the chip from being appended
*/
    $log.info("Requested tag:", chip, "total:", $scope.chips);

    // API CALL
    //search.getData().then();
  }

  $scope.removeChip = function(chip, index) {
    $log.debug("Delete chip, total:", $scope.chips);
  }

  $scope.changePage = function(page) {
    $log.info("Page", page);
  }

}

})();