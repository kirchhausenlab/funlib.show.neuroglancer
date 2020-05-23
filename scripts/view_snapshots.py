import argparse
import os
import random
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

subprocesses = []
for s in snapshots:
    ds_strings = [str(i) for i in args.datasets]
    cmd = ["python", "view_ng.py", "-f", f"{s}", "-d", *ds_strings, "--add_prefix"]
    logger.debug(' '.join(cmd))
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE)
    subprocesses.append(proc)


input()
for proc in subprocesses:
    proc.communicate('stop'.encode())
