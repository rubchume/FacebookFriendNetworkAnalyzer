const electron = require('electron')
    // Module to control application life.
const app = electron.app
    // Module to create native browser window.
const BrowserWindow = electron.BrowserWindow
const path = require('path')
const url = require('url')
    // Keep a global reference of the window object, if you don't, the window will
    // be closed automatically when the JavaScript object is garbage collected.
let mainWindow

function createWindow() {

	var subpy0 = require('child_process').spawn('python', ['./manage.py', 'delete_scan_instances_with_missing_file']);
	var subpy = require('child_process').spawn('python', ['./manage.py', 'runserver']);
	var subpy2 = require('child_process').spawn('python', ['./manage.py', 'process_tasks']);
    var rq = require('request-promise');
    var mainAddr = 'http://localhost:8000';
    var openWindow = function() {
        mainWindow = new BrowserWindow({ width: 800, height: 600 })
        mainWindow.loadURL('http://localhost:8000');
        mainWindow.on('closed', function() {
            mainWindow = null;
            subpy.kill('SIGINT');
            subpy2.kill('SIGINT');
        })
    }
    var startUp = function() {
        rq(mainAddr)
            .then(function(htmlString) {
                console.log('Django iniciado!');
                openWindow();
            })
            .catch(function(err) {
                startUp();
            });
    };
    startUp();
}
// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)
    // Quit when all windows are closed.
app.on('window-all-closed', function() {
    // On OS X it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit()
    }
})
app.on('activate', function() {
        // On OS X it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (mainWindow === null) {
            createWindow()
        }
    })
    // In this file you can include the rest of your app's specific main process
    // code. You can also put them in separate files and require them here.
