morseweb
========
A web client for the Modular OpenRobots Simulation Engine (MORSE)

# Dependencies
+ MORSE **1.3**
+ crossbar.io with Autobahn (for websockets related stuff)
+ Xvfb and LLVMpipe (for launching MORSE in headless mode)

# Instalation
Clone the repo wherever you want. Follow [these](https://www.openrobots.org/morse/doc/latest/headless.html) instructions if you want to run MORSE in headless mode.

# Launching the Simulation
First, import the `examplesim` simulation into MORSE:
```
$ morse import examplesim
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
$ LD_LIBRARY_PATH=/path/to/mesa-11.0.7/build/linux-x86_64/gallium/targets/libgl-xlib DISPLAY=:1 morse run --name nodeA examplesim
```
And in the second one:
```
$ crossbar start --cbdir morseweb/.crossbar
```

# Watching the Simulation
Open a browser and point it to where your server is running, e.g. `example-server.com:8080`. You should see the `empty` environment with an `ATVR` robot and two `SmallTable` objects.

![Image of an example simulation](http://i.imgur.com/NXsbjrW.png)

# Exporting Blender Files
Call the script `utils/export.py` from Blender:
```
$ BLENDER_USER_SCRIPTS=blender_scripts blender -b --addons io_three -P utils/export.py -- args
```

Expected arguments are:
+ `--blend_file`, `-f`: Blender file to export <sup id="a1">[1](#f1)</sup>
+ `--in_directory`, `-i`: Export all Blender files from this directory <sup id="a1">[1](#f1)</sup>
+ `--out_directory`, `-o`: Output destination <sup id="a2">[2](#f2)</sup>

# Loading Passive Objects
At the moment, if you want to load passive objects into a scene, you should name your objects as follows: `object.name = "<model>_<id>_passive"`
+ `<model>.json` should exist in the `morseweb/web/models` directory.
+ `<id>` in case there are multiple copies of the same object.

```
table = PassiveObject("props/objects", "SmallTable")
table.name = "table_0_passive"
table.translate(2, 2, 0)
table.rotate(z=0.7)
```

# Caveats
+ morseweb depends on [multi-node](http://www.openrobots.org/morse/doc/stable/multinode.html)
 mode of MORSE to track the state of the simulation.
+ There has to be a `FakeRobot` instance with an `ExtraServices` sensor attached in the simulation, so morseweb can call the services it needs to work properly.
+ Only one material per mesh is allowed in the models (see discussion [here](https://github.com/mrdoob/three.js/issues/6731#issuecomment-115308900)).
+ Use [these](http://i.imgur.com/upu855O.png) settings when exporting Blender models to Three.js format **from the GUI**.

# Resources
+ https://www.openrobots.org/morse/doc/latest/headless.html
+ https://github.com/morse-simulator/morse/issues/623
+ http://threejs.org

<b id="f1">1</b> `--blend_file` and `--in_directory` are mutually exclusive. [↩](#a1)<br>
<b id="f2">2</b> Current directory if not set. [↩](#a2)
