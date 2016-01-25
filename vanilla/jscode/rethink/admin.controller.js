(function() {
  'use strict';

angular.module('web')
    .controller('AdminController', AdminController);

function AdminController($scope, $rootScope, $log)
{
  // Init controller
  var self = this;
  $log.debug("ADMIN page controller");

  // Template Directories
  self.templateDir = templateDir;
  self.customTemplateDir = customTemplateDir;
  self.blueprintTemplateDir = blueprintTemplateDir;

  //TABS
  self.selectedTab = null;
  self.onTabSelected = function () {
      $log.debug("Selected", self.selectedTab);
  }

}

})();