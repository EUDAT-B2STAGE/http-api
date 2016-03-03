(function() {
'use strict';

angular.module('web')
    .config(hotkeysConfig)
//angular.module('web').run(formlyConfig)
    .config(uploaderConfig);

function hotkeysConfig(hotkeysProvider) {
  //Disable ngRoute integration to prevent listening for $routeChangeSuccess events
  hotkeysProvider.useNgRoute = false;
}

function uploaderConfig(flowFactoryProvider) {

    flowFactoryProvider.defaults = {
        target: 'http://local.docker:8081/upload',
        permanentErrors:[404, 500, 501]
    };

/*
    // You can also set default events:
    flowFactoryProvider.on('catchAll', function (event) {
      ...
    });
    // Can be used with different implementations of Flow.js
    // flowFactoryProvider.factory = fustyFlowFactory;
*/

}

})();