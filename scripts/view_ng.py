from funlib.show.neuroglancer import add_layer
import argparse
import daisy
import glob
import neuroglancer
import os
import webbrowser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def str_or_none(x):
    """Type to pass python `None` via argparse

    Args:
        x (str)

    Returns:
        str or `None`
    """
    return None if x == 'None' or x == 'none' else x


def view_ng(file_path, datasets, shaders, serve, add_prefix=False):
    if serve:
        neuroglancer.set_server_bind_address('0.0.0.0')
    else:
        neuroglancer.set_server_bind_address()

    viewer = neuroglancer.Viewer()

    if shaders is None:
        shaders = [None] * len(file_path)
    else:
        assert len(shaders) == len(file_path)

    for f, datasets, shaders in zip(file_path, datasets, shaders):

        f = f.rstrip('/')
        name_prefix = '/'.join(f.strip('/').split('/')[-2:])
        arrays = []

        for ds in datasets:
            try:

                logger.debug("Adding %s, %s" % (f, ds))
                a = daisy.open_ds(f, ds)

            except BaseException:

                logger.debug("Didn't work, checking if this is multi-res...")

                scales = glob.glob(os.path.join(f, ds, 's*'))
                logger.debug("Found scales %s" % ([
                    os.path.relpath(s, f)
                    for s in scales
                ],))
                a = [
                    daisy.open_ds(f, os.path.relpath(scale_ds, f))
                    for scale_ds in scales
                ]
            arrays.append(a)

        if shaders is None:
            shaders = [None] * len(datasets)
        else:
            assert len(shaders) == len(datasets)

        with viewer.txn() as s:
            for array, dataset, shad in zip(arrays, datasets, shaders):
                if add_prefix:
                    dataset = os.path.join(name_prefix, dataset)
                add_layer(
                    context=s,
                    array=array,
                    name=dataset,
                    shader=shad
                )

    url = str(viewer)
    logger.info(f"\n\t\t{url}\n")
    webbrowser.open_new_tab(url)

    logger.info("Press ENTER to quit")
    input()


if __name__ == '__main__':
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
        '--shaders',
        '-s',
        type=str_or_none,
        choices=[None, 'rgb', 'mask', 'heatmap', 'probmap'],
        default=None,
        nargs='+',
        action='append',
        help=(
            'The shaders to be used for each dataset. '
            'Defaults to `mask` for single channel, '
            '`rgb` for three channel datasets.'
        )
    )
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Serve neuroglancer on public IP'
    )
    parser.add_argument(
        '--add_prefix',
        action='store_true',
        help='Add a prefix to each dataset name'
    )

    args = parser.parse_args()

    view_ng(
        args.file,
        args.datasets,
        args.shaders,
        args.serve,
        args.add_prefix
    )
