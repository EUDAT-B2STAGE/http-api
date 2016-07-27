(function() {
  'use strict';

  angular.module('web').filter('bytes', Bytes);
  angular.module('web').filter('moment', Moment);
  angular.module('web').filter('moment_unix', MomentUnix);
  angular.module('web').filter('unix_date', Unix2Date);

  var months = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");

  function Bytes() {
      return function(bytes, precision) {
          if (bytes == -1 || isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
          var units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'],
              number = Math.floor(Math.log(bytes) / Math.log(1024));

          if (typeof precision === 'undefined') {
              if (number <= 1) precision = 0;
              else precision = 1;
          }
          return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
      }
  }

  function Unix2Date() {

    function leftPad(i) {
        if (i < 10) {
            i = "0" + i;
        }
        return i;
    }

    function getMonthName(m) {
      if (m < 0) return m
      if (m > 11) return m

      return months[m];
    }

    return function(timestamp) {
      var date = new Date(timestamp * 1000);
      var dateObject = 
                  ('0' + date.getDate()).slice(-2)+ ' ' +
                  getMonthName(date.getMonth()) + ' ' +
                  date.getFullYear() +' - '+ 
                  leftPad(date.getHours()) + ':' +
                  leftPad(date.getMinutes()) + ':' +
                  leftPad(date.getSeconds());
      return dateObject;

    }
  }
  /*uses Moment.js and can apply any Moment.js transform function, such as the popular 'fromNow'*/
  function Moment() {

    return function (input, momentFn /*, param1, param2, ...param n */) {
        var args = Array.prototype.slice.call(arguments, 2),
        momentObj = moment(new Date(input));
        return momentObj[momentFn].apply(momentObj, args);
    };
  }

  function MomentUnix() {

    return function (input, momentFn /*, param1, param2, ...param n */) {
        var args = Array.prototype.slice.call(arguments, 2),
        momentObj = moment.unix(input)
        return momentObj[momentFn].apply(momentObj, args);
    };
  }

})();