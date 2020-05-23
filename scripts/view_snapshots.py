import argparse
import glob
import os
import webbrowser
import random
import logging

import neuroglancer
from funlib.show.neuroglancer import add_layer
import daisy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument(
    '--path',
    '-p',
    type=str,
    help="The path with the snapshots to show")
parser.add_argument(
    '--datasets',
    '-d',
    type=str,
    nargs='+',
    help="The datasets in the containers")
parser.add_argument(
    '--serve',
    '-s',
    action='store_true',
    help='Serve neuroglancer on public IP'
)
parser.add_argument(
    '--number',
    '-n',
    type=int,
    default=10,
    help='show n snapshots at random'
)

args = parser.parse_args()

snapshots = [
    os.path.join(args.path, f)
    for f in os.listdir(args.path)
    if f.endswith('.hdf')
]

snapshots = random.sample(snapshots, args.number)
logger.debug(f'snapshots: {snapshots}')

if args.serve:
    neuroglancer.set_server_bind_address('0.0.0.0')
else:
    neuroglancer.set_server_bind_address()

for f in snapshots:
    # TODO might need to launch each viewer in subprocess
    # TODO use different ports
    viewer = neuroglancer.Viewer()
    name_prefix = '/'.join(f.strip('/').split('/')[-3:])[:-4]
    arrays = []
    for ds in args.datasets:
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
        for array, dataset in zip(arrays, args.datasets):
            add_layer(s, array, os.path.join(name_prefix, dataset))

    url = str(viewer)
    print(url)
    webbrowser.open_new_tab(url)

print("Press ENTER to quit")
input()
