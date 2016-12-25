import argparse

from mosaic import builder
from mosaic import collector


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    collect = subparsers.add_parser('collect')
    collect.add_argument(dest='keywords',
                         help='Keywords passed to Google')
    collect.add_argument('--page-count', dest='page_count', type=int,
                         required=True, help='number of pages to collect')
    collect.add_argument('--data-dir', dest='data_dir', default='./data/',
                         help='defaults to ./data/')

    build = subparsers.add_parser('build')
    build.add_argument(dest='image',
                       help='path to the image to make a mosaic from')
    build.add_argument('-o', dest='output', help='output path')
    build.add_argument('--data-dir', dest='data_dir', default='./data/',
                       help='defaults to ./data/')

    args = parser.parse_args()
    if args.subparser == 'build':
        builder.build(
            image=args.image,
            data_dir=args.data_dir,
            output=args.output
        )
    elif args.subparser == 'collect':
        collector.collect(
            keywords=args.keywords.split(','),
            data_dir=args.data_dir,
            page_count=args.page_count
        )


