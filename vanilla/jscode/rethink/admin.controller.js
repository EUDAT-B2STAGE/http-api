(function() {
  'use strict';

angular.module('web')
    .controller('DialogController', DialogController)
    .controller('AdminController', AdminController)
    .controller('AdminWelcomeController', AdminWelcomeController);



function AdminController($scope, $rootScope, $log, admin, $stateParams, $mdMedia, $mdDialog)
{
  // Init controller
  $log.debug("ADMIN page controller", $stateParams);
  var self = this;
  admin.getData().then(function (out)
  {
       console.log("Admin api:", out);
  });

  //TABS
  self.selectedTab = 0;
  self.onTabSelected = function () {
      $log.debug("Selected", self.selectedTab);
  }
  if ($stateParams.tab && $stateParams.tab != self.selectedTab) {
    console.log("URL TAB is ",$stateParams);
    self.selectedTab = $stateParams.tab;

  }

  // Template Directories
  self.blueprintTemplateDir = blueprintTemplateDir;
}

function AdminWelcomeController($scope, $rootScope, $timeout, $log, admin, $stateParams, $mdMedia, $mdDialog)
{
  $log.debug("Welcome admin controller", $stateParams);
  var self = this;

  self.sectionModels = [
    {
        name: 'Section',
        value: 'New section!',
        description: 'The name for your new welcome section',
        required: true,
        focus: true,
        chars: 50,
    },
    {
        name: 'Description',
        value: 'We will talk about a lot of things',
        description: 'Short description of your section. It will appear in the home page.',
        required: true,
        chars: 500,
    },
    {
        name: 'Content',
        value: 'This explanation is very long',
        description: 'Explanation of the section. It will appear in a separate page.',
    },
  ];

  self.models = [
      {
        'Section': 'First',
        'Description': 'This is editable!',
        'Content': 'This is long editable!!<br>Test',
      },
      {
        'Section': 'Second',
        'Description': 'Try',
        'Content': 'Ehm ... <b>Uhm</b>.',
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

//////////////////////////////////////
// HANDLING THE CREATION OF A DIALOG
  $scope.status = 'Dialog to open';
  self.customFullscreen = $mdMedia('xs') || $mdMedia('sm');

  self.showAdvanced = function(ev) {
    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && self.customFullscreen;
// Open
    $mdDialog.show({
      controller: DialogController,
      templateUrl: blueprintTemplateDir + 'add_section.html',
      parent: angular.element(document.body),
      locals: {
        sectionModels: self.sectionModels,
      },
      targetEvent: ev,
      //clickOutsideToClose:true,
      onComplete: function(){
        // Focus on first textarea
        $timeout(function(){
          angular.element("textarea")[0].focus();
        });
      },
      fullscreen: useFullScreen
    })
// WHEN COMPLETED
    .then(function(answer) {
      $scope.status = "Creating the new element";
      var element = {};
      forEach(self.sectionModels, function(x, i) {
        element[x.name] = x.text;
      });
      console.log("To save", element);
      admin.insert('welcome_section', element).then(function (out) {
        console.log("INSERT", out);
        $scope.status = 'Created';
      });

    }, function() {
      $scope.status = 'New element creation aborted...';
    });
    $scope.$watch(function() {
      return $mdMedia('xs') || $mdMedia('sm');
    }, function(wantsFullScreen) {
      self.customFullscreen = (wantsFullScreen === true);
    });
  };

  // Activate dialog to insert new element if requested by url
  if ($stateParams.new) {
    self.showAdvanced();
  }

}

function DialogController($scope, $rootScope, $mdDialog, sectionModels)
{

  $scope.sectionModels = sectionModels;
  $scope.title = "Add a new element";

  $scope.hide = function() {
    $mdDialog.hide();
  };
  $scope.cancel = function() {
    $mdDialog.cancel();
  };
  $scope.answer = function(model) {
    var valid = true;
    forEach(model, function(x, i) {
      if (x.required && !x.text) {
        valid = false;
      }
    });
    if (valid) {
      $mdDialog.hide("Funziona");
    }
  };
}

})();