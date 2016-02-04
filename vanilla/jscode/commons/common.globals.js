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
var localStorageKey = 'myOwnHistory';

var getHistoryOfAllTimes = function ()
{
    var history = JSON.parse(localStorage.getItem(localStorageKey));
    // Note: localStorageKey is defined in common.globals
    if (history === null)
        history = [];
    return history;
}

var setHistoryOfAllTimes = function (data)
{
    localStorage.setItem(localStorageKey, JSON.stringify(data));
}

var lastRoute = function()
{
    var
        baseRoute = 'welcome',
        routingHistory = getHistoryOfAllTimes();

    // I want to go back.
    // The last route is the current one,
    // so i will go 2 routes back in the history.
    var lastIndex = routingHistory.length - 2;
    if (lastIndex < 0 || !routingHistory[lastIndex]) {
        return baseRoute;
    }
    return routingHistory[lastIndex].state.name;
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