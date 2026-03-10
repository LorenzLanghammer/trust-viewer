const { app, BrowserWindow } = require("electron");
const path = require("path");

app.disableHardwareAcceleration();

app.commandLine.appendSwitch("disable-gpu");
app.commandLine.appendSwitch("no-sandbox");
app.commandLine.appendSwitch("disable-software-rasterizer");
app.commandLine.appendSwitch("disable-dev-shm-usage"); // optional for shared memory issues
app.commandLine.appendSwitch("disable-setuid-sandbox"); // sometimes needed

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });

  win.loadURL("http://localhost:5173");
}

app.whenReady().then(createWindow);
