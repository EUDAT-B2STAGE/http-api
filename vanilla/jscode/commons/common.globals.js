/*********************************
*** GLOBAL FUNCTIONS
**********************************/

// BASE CONFS
var framework = 'materialize';
var templateDirBase = '/static/app/templates/';
var templateDir = templateDirBase + framework + '/';
var customTemplateDir = templateDirBase + 'custom/' + framework + '/';
var blueprintTemplateDir = templateDirBase + 'custom/' + blueprint + '/';

// HISTORY GLOBAL OBJECT
var temporaryRoutingHistory = [];

var lastRoute = function() {

    var baseRoute = 'welcome';
    // I want to go back.
    // The last route is the current one,
    // so i will go 2 routes back in the history.
    var lastIndex = temporaryRoutingHistory.length - 2;
    if (lastIndex < 0 || !temporaryRoutingHistory[lastIndex]) {
        return baseRoute;
    }

    return temporaryRoutingHistory[lastIndex].state.name;
}

/*
var projectInfo = {
    name: "RestAngulask",
    description: "Angularjs meets Flask",
}
*/

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
// OTHERS
Object.prototype.hasOwnProperty = function(property) {
    return typeof this[property] !== 'undefined';
};

// TO FIX
function checkApiResponseTypeError(obj) {
  if ( (! obj) ||
      (typeof obj == 'string')  ||
      (obj.hasOwnProperty('message')))
  {
    return true;
  }
}

function setScopeError(message, log, scope) {
  log.error(message);
  scope.error = "Service down...";
}

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + angular.lowercase(this.slice(1));
}

/////////////////////////////////