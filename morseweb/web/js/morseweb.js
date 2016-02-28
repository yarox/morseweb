"use strict";


var container = document.getElementById("container"),
    pRealTime = document.getElementById("realtime"),
    pSimTime = document.getElementById("simtime"),
    pFactor = document.getElementById("factor"),

    timeOptions = {forceLength: true, trim: false},
    timeFormat = 'dd:hh:mm:ss',

    robotNames = [], robots = [],

    camera, scene, light, renderer, controls,
    sceneInfo,
    wsuri;


if (document.location.origin == "file://") {
  wsuri = "ws://127.0.0.1:8080/ws";
} else {
  wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") +
           "//" + document.location.host + "/ws";
}

var connection = new autobahn.Connection({
  realm: "realm1",
  url: wsuri
});

connection.onopen = function(session, details) {
  console.log("Connected");

  // Get scene elements
  session.call("com.simulation.get_scene").then(
    function(res) {
      console.log("get_scene() result:", res);
      sceneInfo = res;

      // Subscribe to simulation updates
      session.subscribe("com.simulation.update", onUpdate).then(
        function(sub) {
          console.log("subscribed to topic", "com.simulation.update");

          init();
          animate();
        },
        function(err) {
          console.log("failed to subscribe to topic", err);
        }
      );
    },
    function(err) {
      console.log("get_scene() error:", err);
    }
  );
};

connection.onclose = function(reason, details) {
  console.log("Connection lost:", reason);
}

connection.open();

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
  var environmentModel = `models/${sceneInfo.environment}.json`;

  loader.load(environmentModel, function(object) {
    console.log("environment loaded", object);

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
      var itemModel = `models/${item.model}.json`;

      loader.load(itemModel, function(object) {
        console.log("object loaded", object);
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

function onUpdate(args, kwargs, details) {
  updateTime(args[0]["__time"]);
  updatePose(args[0]);
}

function updateTime(time) {
  var real = moment.duration(time[2], "seconds");
  var sim = moment.duration(time[0], "seconds");

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
  // Blender and three.js have different coordinate systems, so we have to make
  // some adjustments in order to move the objects properly.

  object.position.set(-position[0], position[2], position[1]);
  object.rotation.set(rotation[0], rotation[2], rotation[1]);
}

function quaternionToEuler(items) {
  var quaternion = new THREE.Quaternion(...items),
      rotation = new THREE.Euler().setFromQuaternion(quaternion);

  return [rotation.x, rotation.y, rotation.z];
}
