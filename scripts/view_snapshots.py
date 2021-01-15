import argparse
import os
import random
import logging
import subprocess
import re
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument(
    '--path',
    '-p',
    type=str,
    help="The path with the snapshots to show.")
parser.add_argument(
    '--datasets',
    '-d',
    type=str,
    nargs='+',
    help="The datasets in the containers.")
parser.add_argument(
    '--serve',
    '-s',
    action='store_true',
    help='Serve neuroglancer on public IP.'
)
parser.add_argument(
    '--number',
    '-n',
    type=int,
    default=10,
    help='Show n snapshots at random.'
)
parser.add_argument(
    '--start',
    type=int,
    default=0,
    help="Lower limit iteration for random sampling."
)
parser.add_argument(
    '--stop',
    type=int,
    default=sys.maxsize,
    help='Upper limit iteration for random sampling.'
)

args = parser.parse_args()

regex = r'(\d+)\.(hdf|zarr)'
snapshots = [
    os.path.join(args.path, f)
    for f in os.listdir(args.path)
    if re.search(regex, f)
]

snapshots = [
    s for s in snapshots
    if int(re.search(regex, s)[1]) >= args.start
    and int(re.search(regex, s)[1]) <= args.stop
]

snapshots = sorted(random.sample(snapshots, min(args.number, len(snapshots))))
logger.debug(f'snapshots: {snapshots}')

subprocesses = []
for s in snapshots:
    ds_strings = [str(i) for i in args.datasets]
    cmd = [
        "python",
        "~/code/src/funlib.show.neuroglancer/scripts/view_ng.py",
        "-f",
        f"{s}",
        "-d",
        *ds_strings,
        "--add_prefix"]
    logger.debug(' '.join(cmd))
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE)
    subprocesses.append(proc)
    time.sleep(0.5)


input()
for proc in subprocesses:
    proc.communicate('stop'.encode())
