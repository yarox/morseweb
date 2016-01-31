
var container = document.getElementById("container"),
    robots = {},
    wsuri,
    camera, scene, renderer, controls,
    sceneInfo, startTime;

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

  // Get simulation start time
  session.call("com.simulation.get_start_time").then(
    function(res) {
      console.log("get_start_time() result:", res);
      startTime = moment.unix(res);

      // Subscribe to simulation elapsed time
      session.subscribe("com.simulation.time", onTime).then(
        function(sub) {
          console.log("subscribed to time");
        },
        function(err) {
          console.log("failed to subscribe to topic", err);
        }
      );
    },
    function(err) {
      console.log("get_start_time() error:", err);
    }
  );

  // Get scene elements
  session.call("com.simulation.get_scene").then(
    function(res) {
      console.log("get_scene() result:", res);
      sceneInfo = res;

      // Subscribe to each robot position
      session.subscribe("com..pose", onPose, { match: "wildcard" }).then(
        function(sub) {
          console.log("subscribed to topic");

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
  console.log("Connection lost: " + reason);
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

    // Load the robots from the simulation
    sceneInfo.robots.forEach(function(robot) {
      var robotModel = `models/${robot.model}.json`;

      loader.load(robotModel, function(object) {
        console.log("robot loaded", object);
        robots[robot.name] = object;
        scene.add(object);
      });
    });
  });
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);

  render();
}

function animate() {
  requestAnimationFrame(animate);
  render();
}

function render() {
  renderer.render(scene, camera);
}

function onTime(args, kwargs, details) {
  var options = {forceLength: true, trim: false};
  var format = 'dd:hh:mm:ss';

  var pRealTime = document.querySelector(".time .real");
  var pSimTime = document.querySelector(".time .simulation");

  var real = moment.duration(moment.unix(args[0].realitime) - startTime);
  var sim = moment.duration(moment.unix(args[0].simtime) - startTime);

  pRealTime.innerHTML = `Real Time: ${real.format(format, options)}`;
  pSimTime.innerHTML = `Simulation Time: ${sim.format(format, options)}`;
}

function onPose(args, kwargs, details) {
  var robot = robots[kwargs.name];
  updateRobotPosition(robot, args[0]);
}

function updateRobotPosition(robot, data) {
  // Blender and three.js have different coordinate systems, so we have to make
  // some adjustments in order to move the objects properly.
  robot.position.x = -data.x;
  robot.position.y = data.z;
  robot.position.z = data.y;

  robot.rotation.x = data.roll;
  robot.rotation.y = data.yaw;
  robot.rotation.z = data.pitch;
}
