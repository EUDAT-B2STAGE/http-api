(function() {
  'use strict';

// DISABLE THE MAIN RUN
angular.module('web').run(formRun);

function formRun($log, editableOptions, editableThemes, formlyConfig)
{
    $log.debug('Run the app :)');

/*
XEDITABLE
https://github.com/vitalets/angular-xeditable/issues/232
*/

  editableThemes['angular-material'] =
  {
    formTpl:      '<form class="editable-wrap"></form>',
    noformTpl:    '<span class="editable-wrap"></span>',
    controlsTpl:  '<md-input-container class="editable-controls" '+
        'ng-class="{\'md-input-invalid\': $error}"></md-input-container>',
    inputTpl:     '',
    errorTpl:     '<div ng-messages="{message: $error}"><div class="editable-error" ng-message="message">{{$error}}</div></div>',
    buttonsTpl:   '<span class="editable-buttons"></span>',
    submitTpl:    '<md-button type="submit" class="md-primary">save</md-button>',
    cancelTpl:    '<md-button type="button" class="md-warn" ng-click="$form.$cancel()">cancel</md-button>',
  };

  editableOptions.theme = 'angular-material';


/*
    // Add xeditable type to formly
    formlyConfig.setType({
      extends: 'input',
      template:
        '<div>' +
            '<span editable-text="model[options.key]" e-name="{{::id}}">' +
                '{{ model[options.key] || "empty" }}' +
            '</span>' +
        '</div>',
      name: 'editableInput'
    });
*/

}

})();
