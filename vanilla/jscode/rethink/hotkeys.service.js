(function() {
  'use strict';

angular.module('web')
    .service('extrakeyshortcuts', ExtraKeysService);

function ExtraKeysService($timeout, $state) {

  var self = this;

// NO EXTRA KEYS AT THE MOMENT :/

/*
  self.search = function(event, controller) {
    event.preventDefault();
    $timeout(function () {
        $state.go('logged.specialsearch');
    }, 10);
  }

  self.exitSearch = function(event, controller) {
    event.preventDefault();
    controller.goToLastRoute();
  }

  self.openHistorySidebar = function(event, controller) {
    event.preventDefault();
    controller.open();
  }
*/


/*
  self.scrollListDown = function(event, controller) {
    event.preventDefault();
    if (isNaN(controller.focusPosition)) controller.focusPosition = 1;
    else if (controller.focusPosition < controller.list.length)
      controller.focusPosition = controller.focusPosition + 1;
  }

  self.scrollListUp = function(event, controller) {
    event.preventDefault();
    if (isNaN(controller.focusPosition)) controller.focusPosition = 1;
    else if (controller.focusPosition > 0)
      controller.focusPosition = controller.focusPosition -1;
  }

  self.getSelectedID = function(controller) {
    if (isNaN(controller.focusPosition)) return 0;
    return controller.list[controller.focusPosition-1].id;
  }

  self.openEntry = function(event, controller, $state, newstateName, newstateParameters)
  {
    event.preventDefault();
    if (isNaN(controller.focusPosition)) console.log("No entry selected");
    else {
      $state.go(newstateName, newstateParameters);
    }
  }
*/

}

})();