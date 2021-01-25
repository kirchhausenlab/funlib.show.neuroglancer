from funlib.show.neuroglancer import add_layer
import argparse
import daisy
import glob
import neuroglancer
import os
import webbrowser

parser = argparse.ArgumentParser()
parser.add_argument(
    '--file',
    '-f',
    type=str,
    action='append',
    help="The path to the container to show")
parser.add_argument(
    '--datasets',
    '-d',
    type=str,
    nargs='+',
    action='append',
    help="The datasets in the container to show")
parser.add_argument(
    '--serve',
    '-s',
    action='store_true',
    help='Serve neuroglancer on public IP'
)

args = parser.parse_args()

if args.serve:
    neuroglancer.set_server_bind_address('0.0.0.0')
else:
    neuroglancer.set_server_bind_address()

viewer = neuroglancer.Viewer()

for f, datasets in zip(args.file, args.datasets):

    f = f.rstrip('/')
    arrays = []
    for ds in datasets:
        try:

            print("Adding %s, %s" % (f, ds))
            a = daisy.open_ds(f, ds)

        except BaseException:

            print("Didn't work, checking if this is multi-res...")

            scales = glob.glob(os.path.join(f, ds, 's*'))
            print("Found scales %s" % ([
                os.path.relpath(s, f)
                for s in scales
            ],))
            a = [
                daisy.open_ds(f, os.path.relpath(scale_ds, f))
                for scale_ds in scales
            ]
        arrays.append(a)

    with viewer.txn() as s:
        for array, dataset in zip(arrays, datasets):
            add_layer(s, array, dataset)

url = str(viewer)
print(url)
webbrowser.open_new_tab(url)

print("Press ENTER to quit")
input()
