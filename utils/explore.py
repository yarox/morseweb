from os.path import basename, splitext, join, commonprefix

import logging
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_objects(blend_file, same_prefix=True):
    # Clear any object present in Blender
    try:
        bpy.ops.object.select_all(action="SELECT")
    except RuntimeError as e:
        pass
    else:
        bpy.ops.object.delete(use_global=False)

    # Load the Blender file to export
    bpy.ops.wm.open_mainfile(filepath=blend_file)

    if same_prefix:
        # Return every parent object in the scene where their children share the
        # same prefix
        objects = []

        for obj in bpy.context.scene.objects:
            prefix = commonprefix([obj.name] + [c.name for c in obj.children])

            if (obj.parent is None) and (prefix == obj.name):
                objects.append(obj.name)
    else:
        # Return every parent object in the scene
        objects = [obj.name for obj in bpy.context.scene.objects
                            if obj.parent is None]

    return objects

def usage():
    msg = "usage: {} blend_file [blend_file ...]"
    return msg.format(basename(sys.argv[0]))


try:
    import bpy
except ImportError:
    print("\nMUST be called as follows:",
          "\nBLENDER_USER_SCRIPTS=blender_scripts "
          "blender -b --addons io_three -P utils/export.py -- args\n")
    export_threejs = print


if __name__ == "__main__":
    try:
        args = sys.argv[sys.argv.index("--") + 1:]
    except ValueError:
        args = sys.argv[1:]

    if len(args) >= 1:
        blend_files = args[0:]
    else:
        sys.exit(usage())

    for blend_file in blend_files:
        for obj in list_objects(blend_file):
            s = "### {} {} $$$".format(obj, blend_file)
            print(s)
