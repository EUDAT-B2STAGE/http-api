(function() {
  'use strict';

angular.module('web')
    .controller('AdminController', AdminController);

function AdminController($scope, $rootScope, $log, admin)
{
  // Init controller
  var self = this;
  $log.debug("ADMIN page controller");

  self.sectionModel = [
    {
        name: 'Section',
        value: 'New section!',
        description: 'The name for your new welcome section',
    },
    {
        name: 'Description',
        value: 'We will talk about a lot of things',
        description: 'Short description of your section. It will appear in the home page.',
    },
  ];

  self.models = [
      {
        name: 'First',
        value: 'This is editable!',
        description: 'Try the incredible emotions of writing',
      },
      {
        name: 'Second',
        value: 'Agaiin!',
      },
  ];
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