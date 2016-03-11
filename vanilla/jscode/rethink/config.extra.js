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
/* THIS HAS TO BE FIXED */
        // CHECK WHAT WE DO IN COMMON.API.JS
        //target: 'http://local.docker:8081/api/upload',

        target: function (FlowFile, FlowChunk, isTest) {
            console.log("FLow file is ", FlowFile);
            return
                'http://' +
                'local.docker:8081/api' +
                '/upload';
                //+ FlowFile.record;
        }

/* THIS HAS TO BE FIXED */

        //permanentErrors:[404, 500, 501]
    };

}

})();