(function() {
  'use strict';

angular.module('web')
    .controller('WelcomeController', WelcomeController);

function WelcomeController($scope, $log)
{
  $log.debug("Welcome controller", $stateParams);
  self.init = 'example';
}

})();