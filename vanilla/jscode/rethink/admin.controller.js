(function() {
  'use strict';

angular.module('web')
    .controller('AdminController', AdminController);

function AdminController($scope, $rootScope, $log, admin)
{
  // Init controller
  var self = this;
  $log.debug("ADMIN page controller");

  self.model = {
    name: 'This is editable!'
  };
/*
  self.options = {};
  self.fields = [
    {
      key: 'text',
      type: 'editableInput',
      templateOptions: {
        label: 'Text'
      }
    }
  ];
  self.originalFields = angular.copy(self.fields);
*/

  // function definition
  self.saveForm = function () {
    console.log("MODEL", self.model);
  }

/*
  self.onSubmit = function () {
    self.options.updateInitialValue();
    console.log("MODEL", self.model);
  }
*/

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