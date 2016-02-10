(function() {
  'use strict';

angular.module('web')
    .controller('SearchController', SearchController);

function SearchController($scope, $rootScope, $log, $state, search)
{
  // Init
  $log.info("Ready to search");
  var self = this;

  $scope.data = {};
  $scope.chips = [];

// https://material.angularjs.org/latest/demo/chips
  $scope.newChip = function(chip) {
    $log.info("Requested tag:", chip, "total:", $scope.chips);
    // API CALL
    //search.getData().then();
  }

  $scope.removeChip = function(chip, index) {
    $log.debug("Delete chip, total:", $scope.chips);
  }

}

})();