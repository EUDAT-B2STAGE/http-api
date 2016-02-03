(function() {
  'use strict';

angular.module('web')
    .service('keyshortcuts', HotkeysService);

function HotkeysService($timeout, $state) {

  var self = this;

  self.search = function(event, controller) {
    event.preventDefault();
    $timeout(function () {
        $state.go('logged.specialsearch');
    }, 10);
  }

  self.exitSearch = function(event, controller) {
    event.preventDefault();
    $timeout(function () {
// YOU NEED A FUNCTION TO REMEMBER POSITION
        $state.go('welcome');
        //$state.go('logged.explore');
    }, 10);
  }

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

}

})();