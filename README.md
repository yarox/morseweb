morseweb
========
A web client for the Modular OpenRobots Simulation Engine (MORSE)

# Dependencies
+ **crossbar.io** with **Autobahn** (for websockets related stuff)
+ **Xvfb** and **LLVMpipe** (for launching **MORSE** in headless mode)

# Instalation
Follow [these](https://www.openrobots.org/morse/doc/latest/headless.html) instructions if you want to enable **MORSE** in "headless" mode.

# Launching the Simulation
## Regular Mode
Open two terminals. In the first one run:
```
$ morse run examplesim
```
And in the second one:
```
$ crossbar start --cbdir /path/to/morseweb/morseweb/.crossbar
```

## Headless Mode
Open two terminals. In the first one run:
```
$ Xvfb -screen 0 100x100x24 :1 &
$ LD_LIBRARY_PATH=/path/to/mesa-11.0.7/build/linux-x86_64/gallium/targets/libgl-xlib DISPLAY=:1 morse run examplesim
```
And in the second one:
```
$ crossbar start --cbdir /path/to/morseweb/morseweb/.crossbar
```

# Watching the Simulation
Open a browser and point it to where your server is running, e.g. `example-server.com:8080`. You should see the `empty` environment with an `ATVR` robot standing in the middle.

![Image of an example simulation](http://i.imgur.com/aAkIpAx.png)

# Caveats
+ Simulated robots need to have a `Pose` sensor attached, so **morseweb** can track their positions.
+ There has to be a `FakeRobot` instance with an `ExtraServices` sensor attached in the simulation, so **morseweb** can call the services it needs to work properly.
+ Only one material per mesh is allowed in the models (see discussion [here](https://github.com/mrdoob/three.js/issues/6731#issuecomment-115308900)).
+ Use [these](http://i.imgur.com/upu855O.png) settings when exporting **Blender** models to **Three.js** format.

# Resources
+ https://www.openrobots.org/morse/doc/latest/headless.html
+ https://github.com/morse-simulator/morse/issues/623
+ http://threejs.org
