(function() {
  'use strict';

/* Define another module?
console.log('PRE');
angular.module('blueprint', ['ui.router']);
console.log('POST');
*/

  angular
    .module('web', [
// BASE
        //'ngAnimate',
        'ngSanitize',
// ROUTING
        'ui.router', //'ngRoute',
// BOOTSTRAP
        //'mgcrea.ngStrap',
// OFFICIAL MATERIAL
        'ngMaterial',
// MATERIAL DESIGN
        'ui.materialize',
// AUTH
        'satellizer',
// KEYBOARD SHORTCUTS
        'cfp.hotkeys',
// FORMS FROM JSON SCHEMAS
        'formly',
        'formlyBootstrap',
//////////////////////////////////////
/* Custom */

// THE LOADING BAR
        //'angular-loading-bar',
        //'cfp.loadingBar',
// IMAGES LAZ LOAD
        // 'angularLazyImg',
// MAKE DATA TREE explorer
        // 'treeControl',
// DRAG AND DROP
        // 'angular-sortable-view',
// EDITABLE FORMS
        // 'xeditable',
// RESTARTABLE UPLOAD
        // 'flow',

/* Custom end */
//////////////////////////////////////

    ]);

})();
