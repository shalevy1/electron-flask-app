const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;

const crashReporter = require('electron').crashReporter;


crashReporter.start({
 productName    : 'Flask-App',
 companyName    : 'xPlatform.rocks',
 submitURL      : '',
 uploadToServer : true
});


let mainWindow = null;
let subpy = null;
let rq = null;
let mainAddr =null;
let openWindow = null;
app.on('window-all-closed', function() {
  //if (process.platform != 'darwin') {
    app.quit();
  //}
});

app.on('ready', function() {
  // call python?
  let subpy = require('child_process').spawn('python', ['./run.py']);
  let rq = require('request-promise');
  let mainAddr = 'http://localhost:5000';

  let openWindow = function() {
    mainWindow = new BrowserWindow( { width: 800, height: 600 });
    // mainWindow.loadURL('file://' + __dirname + '/index.html');
    mainWindow.loadURL('http://localhost:5000');
    mainWindow.on('closed', function() {
      mainWindow = null;
      subpy.kill('SIGINT');
    });
  };

  let startUp = function() {
    rq(mainAddr)
      .then(function(htmlString) {
        console.log('server started!');
        openWindow();
      })
      .catch(function(err) {
        //console.log('waiting for the server start...');
        startUp();
      });
  };

  // fire!
  startUp();
});
