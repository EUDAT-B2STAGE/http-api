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
    controller.goToLastRoute();
  }

  self.openHistorySidebar = function(event, controller) {
    event.preventDefault();
    controller.open();
  }

}

})();
