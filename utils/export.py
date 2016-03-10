from os.path import basename, splitext, join
from itertools import zip_longest

import argparse
import logging
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_threejs(blend_file, json_file, object_name=None):
    # Clear any object present in Blender
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Load the Blender file to export
    bpy.ops.wm.open_mainfile(filepath=blend_file)

    if object_name is not None:
        # Select the object and its children
        bpy.ops.object.select_pattern(pattern=object_name, extend=False)
        bpy.ops.object.select_hierarchy(direction="CHILD", extend=True)

        # Invert the selection and delete everything but the object passed as a
        # parameter
        bpy.ops.object.select_all(action="INVERT")
        bpy.ops.object.select_hierarchy(direction="CHILD", extend=True)
        bpy.ops.object.delete(use_global=False)

    # An object must be selected for the exporter to work
    bpy.context.scene.objects.active = bpy.data.objects[0]

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


parser = argparse.ArgumentParser(description="Export Blender file to Three.js' \
                                              JSON format.")

parser.add_argument("blend_files", type=str, nargs="+",
                    help="Blender files to export")
parser.add_argument("--object_names", "-n", type=str, nargs="+", default=[],
                    help="Objects to export")
parser.add_argument("--out_directory", "-o", type=str, default="",
                    help="Output destination")


if __name__ == "__main__":
    try:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    except ValueError:
        args = parser.parse_args()

    for blend_file, object_name in zip_longest(args.blend_files, args.object_names):
        logger.info("Exporting '%s' from '%s'...", object_name, blend_file)

        json_file = join(args.out_directory, object_name + ".json")
        filename = basename(splitext(blend_file)[0])

        if filename == object_name:
            object_name = None

        try:
            export_threejs(blend_file, json_file, object_name)
        except RuntimeError as e:
            logger.warning(e)
