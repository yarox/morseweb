from os.path import basename, splitext, join

import argparse
import glob
import sys


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
                         option_faces=True
                        )

try:
    import bpy
except ImportError:
    print("\nMUST be called as follows:",
          "\nBLENDER_USER_SCRIPTS=blender_scripts "
          "blender -b --addons io_three -P utils/export.py -- args\n")
    export_threejs = print


parser = argparse.ArgumentParser(description="Export Blender file to Three.js' \
                                              JSON format.")
group = parser.add_mutually_exclusive_group()
group.add_argument("--blend_file", "-f", default="", type=str,
                    help="Blender file to export")
group.add_argument("--in_directory", "-i", default="", type=str,
                    help="Export Blender files from this directory")
parser.add_argument("--out_directory", "-o", default="", type=str,
                    help="Output destination")


if __name__ == "__main__":
    try:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    except ValueError:
        args = parser.parse_args()

    if args.blend_file:
        filename = basename(splitext(args.blend_file)[0])
        json_file = join(args.out_directory, filename + ".json")
        export_threejs(args.blend_file, json_file)

    elif args.in_directory:
        in_directory = join(args.in_directory, "*.blend")

        for blend_file in glob.iglob(in_directory):
            filename = basename(splitext(blend_file)[0])
            json_file = join(args.out_directory, filename + ".json")
            export_threejs(blend_file, json_file)
    else:
        parser.print_help()
