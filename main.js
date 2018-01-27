const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;

const crashReporter = require('electron').crashReporter;
const PY_DIST_FOLDER = 'dist'
const PY_FOLDER = 'run'
const PY_MODULE = 'run' // without .py suffix
const path = require('path')
const guessPackaged = function() {
  const fullPath = path.join(__dirname, PY_DIST_FOLDER)
  return require('fs').existsSync(fullPath)
};

const getScriptPath = function () {
  if (!guessPackaged()) {
    return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
  }
  if (process.platform === 'win32') {
    return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE + '.exe')
  }
  return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE)

}

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
let pyProc = null;


app.on('window-all-closed', function() {
  //if (process.platform != 'darwin') {
    app.quit();
  //}
});

app.on('ready', function() {
  // call python?
  let script = getScriptPath()
  console.log(script)

  subpy = require('child_process').execFile(script);
  console.log(subpy != null)
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
