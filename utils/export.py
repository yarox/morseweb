from os.path import basename, splitext, join

import logging
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_threejs(blend_file, json_file):
    # Clear any object present in Blender
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Load the Blender file to export
    bpy.ops.wm.open_mainfile(filepath=blend_file)

    # We must set one active object for the exporter to work
    obj = bpy.data.objects[0]
    bpy.context.scene.objects.active = obj

    # Call the three.js exporter
    bpy.ops.export.three(filepath=json_file,
                         option_index_type='Uint16Array',
                         option_apply_modifiers=True,
                         option_face_materials=True,
                         option_export_scene=True,
                         option_materials=True,
                         option_uv_coords=True,
                         option_vertices=True,
                         option_normals=True,
                         option_faces=True)

def usage():
    msg = "usage: {} out_directory blend_file [blend_file ...]"
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

    if len(args) >= 2:
        out_directory = args[0]
        blend_files = args[1:]
    else:
        sys.exit(usage())

    for blend_file in blend_files:
        logger.info("Exporting '%s'...", blend_file)

        filename = basename(splitext(blend_file)[0])
        json_file = join(out_directory, filename + ".json")
        export_threejs(blend_file, json_file)
