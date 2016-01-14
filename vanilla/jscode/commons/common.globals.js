/*********************************
*** GLOBAL FUNCTIONS
**********************************/

// BASE CONFS
var framework = 'materialize';
var templateDirBase = '/static/app/templates/';
var templateDir = templateDirBase + framework + '/';
var customTemplateDir = templateDirBase + 'custom/' + framework + '/';

/////////////////////////////////
// FOR EACH AUTO IMPLEMENTATION
 //https://toddmotto.com/simple-foreach-implementation-for-objects-nodelists-arrays-with-automatic-type-looping/
var forEach = function (collection, callback, scope) {
  if (Object.prototype.toString.call(collection) === '[object Object]') {
    for (var prop in collection) {
      if (Object.prototype.hasOwnProperty.call(collection, prop)) {
        callback.call(scope, collection[prop], prop, collection);
      }
    }
  } else {
    for (var i = 0; i < collection.length; i++) {
      callback.call(scope, collection[i], i, collection);
    }
  }
};


/////////////////////////////////
// ROUTES AND AUTHENTICATION

// Ui Resolve + Satellizer to authenticate
// original source http://j.mp/1VnxlQS heavily modified

// Check authentication via Token
function _redirectIfNotAuthenticated($state, $auth, $timeout, $log, api)
{
    return api.verify(true).then(function(response){
      // Token is available and API confirm that is good
      if (response && $auth.isAuthenticated()) {
        return true;
      }
      var state = 'login';
      // API not reachable
      if (response === null) {
        state = 'offline';
      }
      // Not logged or API down
      $timeout(function () {
          // redirect
          $log.error("Failed resolve");
          $state.go(state);
          return false;
      });
    });
}

// Skip authentication
// Check for API available
function _skipAuthenticationCheckApiOnline($state, $timeout, $auth, api)
{
    return api.verify()
      .then(function(response){

        // API available
        if (response) {
          // Login request but Already logged
          if ($state.current.name == 'login' && $auth.isAuthenticated()) {
            $timeout(function () {
                $state.go('logged');
            });
          }
          return response;
        }
        // Not available
        $timeout(function () {
            $state.go('offline');
            return response;
        });
    });
}

/////////////////////////////////
// OTHERS
Object.prototype.hasOwnProperty = function(property) {
    return typeof this[property] !== 'undefined';
};

// TO FIX
function checkApiResponseTypeError(obj) {
  if (
      (! obj) ||
      (typeof obj == 'string')  ||
      (obj.hasOwnProperty('message'))) {
    return true;
  }
}

function setScopeError(message, log, scope) {
  log.error(message);
  scope.error = "Service down...";
}

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

/////////////////////////////////