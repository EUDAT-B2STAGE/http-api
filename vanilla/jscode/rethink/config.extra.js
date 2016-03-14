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
        // Found out about in:
        //https://github.com/flowjs/flow.js/issues/57#issuecomment-62300498
        target: function (FlowFile, FlowChunk, isTest) {
            //console.log("FLow file is ", FlowFile);
            return
                apiUrl +
                '/upload';
                //+ FlowFile.record;
        }

        //permanentErrors:[404, 500, 501]
    };

}

})();