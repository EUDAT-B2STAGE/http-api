// JINJA TEMPLATE (not AngularJs syntax)

// Choose your blueprint
var blueprint = '{{name}}';

// Note: remember to define '{{name}}Routes' or you will get
// a strange injection error!

// Time to wait before initial page load
var timeToWait = {{time}}; // measured in ms

// Api URI
var apiPort = 8081;
var serverUrl = '{{api_url}}'.slice(0, -1);
var apiUrl = serverUrl + ':' + apiPort + '/api';
var authApiUrl = serverUrl + ':' + apiPort + '/auth';

var welcomeTemplate = {{js_template}};
