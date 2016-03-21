(function() {
  'use strict';

angular.module('web')
    .controller('ZoomController', ZoomController);

function ZoomController($scope, $log)
{
  // Init
  var self = this;
  $log.info("The zoom");

  self.myvar = 'test';

  console.log("TEST1");

  Z.showImage(
    "myContainer",
    //"files/documents/collocazione_3_page001" ,
    "static/uploads/Screenshot_2014-03-04_19.06.21"
    //,
    // "zToolbarPosition=2&zFullPageInitial=1&zSkinPath=Assets/Skins/Dark"
    // // options
    // + "&zNavigatorFit=1&zNavigatorWidth=80&zNavigatorHeight=80"
    // + "&zNavigatorVisible=3&zInitialZoom=0&zLogoVisible=0"
    // + "&zToolbarVisible=1&zLogoVisible=0"
    // + "&zSliderVisible=1&zProgressVisible=0&zTooltipsVisible=0"
  );

  console.log("TEST2");

}

})();
