(function() {
  'use strict';

angular.module('web')
    .controller('AdminController', AdminController);

function AdminController($scope, $rootScope, $log, admin)
{
  // Init controller
  var self = this;
  $log.debug("ADMIN page controller");
  self.model = {};

  // Template Directories
  self.templateDir = templateDir;
  self.customTemplateDir = customTemplateDir;
  self.blueprintTemplateDir = blueprintTemplateDir;

  admin.getData();

  //TABS
  self.selectedTab = null;
  self.onTabSelected = function () {
      $log.debug("Selected", self.selectedTab);
  }

}

})();