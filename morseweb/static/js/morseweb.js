"use strict";

function startScene(sceneReady, sceneUrl) {

  var container = document.getElementById("container"),
      pRealTime = document.getElementById("realtime"),
      pSimTime = document.getElementById("simtime"),
      pFactor = document.getElementById("factor"),

      socket = io.connect(),

      timeOptions = {forceLength: true, trim: false},
      timeFormat = "dd:hh:mm:ss",

      robotNames = [], robots = [],

      camera, scene, light, renderer, controls,
      sceneInfo;


  socket.on("connect", function() {
    console.log("Connected to", socket.io.uri);
  });

  socket.on("simulator.status", function(msg) {
    console.log(msg.data);
  });

  if (sceneReady) {
    getScene(sceneUrl);
  } else {
    socket.on("simulator.ready", function() {
      getScene(sceneUrl)
    });
  }


  function getScene(url){
    $.get(url, function(data) {
      console.log("Scene loaded", data);
      sceneInfo = data;

      socket.on("simulator.update", onUpdate);

      init();
      animate();
    });
  }

  function init() {
    // Handle window resize
    window.addEventListener("resize", onWindowResize, false);

    // Renderer
    renderer = new THREE.WebGLRenderer();

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setClearColor(0xEEEEEE);
    container.appendChild(renderer.domElement);

    // Scene
    scene = new THREE.Scene();
    light = new THREE.AmbientLight(0xffffff);

    var gridHelper = new THREE.GridHelper(10, 1);
    var axisHelper = new THREE.AxisHelper(5);

    gridHelper.setColors(0xEEEEEE, 0x555555);

    scene.add(gridHelper);
    scene.add(axisHelper);
    scene.add(light);

    // Camera
    var aspect = window.innerWidth / window.innerHeight;

    camera = new THREE.PerspectiveCamera(70, aspect, 1, 1000);
    camera.position.set(sceneInfo.camera_position.x,
                        sceneInfo.camera_position.y,
                        sceneInfo.camera_position.z);

    // Controls
    controls = new THREE.EditorControls(camera);

    // Load the environment
    var loader = new THREE.ObjectLoader();
    var environmentModel = `static/json/${sceneInfo.environment}.json`;

    loader.load(environmentModel, function(object) {
      console.log("Environment loaded", object);

      // Calculate camera parameters in order to be able to see the whole
      // scene from it. See: http://stackoverflow.com/q/2866350/1563669
      var distance = camera.position.distanceTo(object.position);
      var box = new THREE.Box3().setFromObject(object);
      var max = Math.max(...box.max.toArray());

      camera.fov = 2 * Math.atan(max / (2 * distance)) * (180 / Math.PI);
      camera.updateProjectionMatrix();
      camera.lookAt(scene.position);

      scene.add(object);

      // Load items from the simulation
      sceneInfo.items.forEach(function(item) {
        var itemModel = `static/json/${item.model}.json`;

        loader.load(itemModel, function(object) {
          console.log("Object loaded", object);
          scene.add(object);

          if (item.type === "robot") {
            robotNames.push(item.name);
            robots.push(object)
          } else if (item.type === "passive") {
            item.rotation = quaternionToEuler(item.rotation)
          } else {
            console.warn("Unknown object", item);
            return;
          }

          updateObject(object, item.position, item.rotation);
        });
      });
    });
  }

  function animate() {
    requestAnimationFrame(animate);
    render();
  }

  function render() {
    renderer.render(scene, camera);
  }

  function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(window.innerWidth, window.innerHeight);

    render();
  }

  function onUpdate(data) {
    updateTime(data.__time);
    updatePose(data);
  }

  function updateTime(time) {
    var real = moment.duration(time[2], "seconds"),
        sim = moment.duration(time[0], "seconds");

    pRealTime.textContent = real.format(timeFormat, timeOptions);
    pSimTime.textContent = sim.format(timeFormat, timeOptions);
    pFactor.textContent = (time[0] / time[2]).toFixed(4);
  }

  function updatePose(poses) {
    for (var name, i = 0; i < robots.length; i++) {
      name = robotNames[i];
      updateObject(robots[i], poses[name][0], poses[name][1]);
    }
  }

  function updateObject(object, position, rotation) {
    // Blender and three.js have different coordinate systems, so we have to
    // make some adjustments in order to move the objects properly.
    object.position.set(-position[0], position[2], position[1]);
    object.rotation.set(rotation[0], rotation[2], rotation[1]);
  }

  function quaternionToEuler(items) {
    var quaternion = new THREE.Quaternion(...items),
        rotation = new THREE.Euler().setFromQuaternion(quaternion);

    return [rotation.x, rotation.y, rotation.z];
  }
}
