morseweb
========
morseweb is a WebGL client for [MORSE](https://www.openrobots.org/morse/doc/stable/morse.html). It's a front-end graphical interface to the simulator and provides visualization of the simulation from a web browser. This means cross-platform support (including mobile devices) and minimal client-side dependencies.

# Dependencies
+ [MORSE](https://www.openrobots.org/morse/doc/stable/user/installation.html#manual-installation) **1.4**
+ crossbar.io with Autobahn (for websockets related stuff)
+ Xvfb and LLVMpipe (for launching MORSE in headless mode)

# Instalation
morseweb is installed on the server-side. Once the server is set up and running, clients can watch the simulation by accessing the server's URL on a web browser.

Clone the repo wherever you want, and follow [these](https://www.openrobots.org/morse/doc/latest/headless.html) instructions if you want to run MORSE in headless mode.

# Launching the Simulation
Import the `examplesim` simulation into MORSE
```
$ morse import examplesim
```
and set the environment variables<sup id="a1">[1](#fn1)</sup> where MORSE will be looking for components:
```
$ export MORSE_ROOT="/usr"
$ export MORSE_RESOURCE_PATH="/path/number/one:/path/number/two"
```

## Regular Mode
Open two terminals. In the first one run:
```
$ multinode_server &
$ morse run --name nodeA examplesim
```
And in the second one:
```
$ crossbar start --cbdir morseweb/.crossbar
```

## Headless Mode
Open two terminals. In the first one run:
```
$ Xvfb -screen 0 100x100x24 :1 &
$ multinode_server &
$ export LD_LIBRARY_PATH=/path/to/mesa-11.0.7/build/linux-x86_64/gallium/targets/libgl-xlib
$ export DISPLAY=:1
$ morse run --name nodeA examplesim
```
And in the second one:
```
$ crossbar start --cbdir morseweb/.crossbar
```

# Watching the Simulation
Open a browser and point it to where your server is running, e.g. `example-server.com:8080`. You should see the `empty` environment with an `ATVR` robot and two `SmallTable` objects.

![Image of an example simulation](http://i.imgur.com/NXsbjrW.png)

# Loading Passive Objects
If you want to load passive objects into a scene you should set the name of the object exactly as the name of the model you're loading:

```
table = PassiveObject("props/objects", "SmallTable")
table.name = "SmallTable"
table.translate(2, 2, 0)
table.rotate(z=0.7)
```

# Caveats
+ morseweb depends on [multi-node](http://www.openrobots.org/morse/doc/stable/multinode.html)
 mode of MORSE to track the state of the simulation.
+ Only one material per mesh is allowed in the models (see discussion [here](https://github.com/mrdoob/three.js/issues/6731#issuecomment-115308900)). But this should be fixed in future releases (see [this](https://github.com/mrdoob/three.js/pull/8087) and [this](https://github.com/mrdoob/three.js/pull/8068)).

# Resources
+ https://github.com/morse-simulator/morse/issues/623
+ http://threejs.org
+ http://gazebosim.org/gzweb

---
<b id="fn1">1</b> `MORSE_ROOT` may be different if you installed MORSE in a custom location. [&#8617;
](#a1)<br>
