(function() {
  'use strict';

///////////////////////////////////////////
///////////////////////////////////////////
/********************/
angular
    .module('web')
    .controller('MainController', MainController)
    .controller('FabButtonController', FabController);

function MainController($scope, $log, $location)
{
    $log.info("Main");
}

//https://material.angularjs.org/latest/demo/fabSpeedDial
function FabController($scope, $log, $timeout)
{
    var self = this;
    $log.info("Fab");

    self.isOpen = false;
    self.tooltipVisible = false;
    self.availableModes = ['md-fling', 'md-scale'];
    self.selectedMode = 'md-scale';
    self.hover = false;

    self.items = [
        { name: "Twitter", icon: "twitter", direction: "bottom" },
        { name: "Facebook", icon: "facebook", direction: "top" },
        { name: "Google Hangout", icon: "hangout", direction: "bottom" }
    ];

      // On opening, add a delayed property which shows tooltips after the speed dial has opened
      // so that they have the proper position; if closing, immediately hide the tooltips
      $scope.$watch('demo.isOpen', function(isOpen) {
        if (isOpen) {
          $timeout(function() {
            $scope.tooltipVisible = self.isOpen;
          }, 600);
        } else {
          $scope.tooltipVisible = self.isOpen;
        }
      });
}

})();