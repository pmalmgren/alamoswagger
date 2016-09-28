#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse
import logging
import os

import parse_model


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(name="alamoswagger")


def get_args():
    parser = argparse.ArgumentParser(description='Add ResponseObjectSerializable protocol conformance to swagger-codegen generated models.')
    parser.add_argument('input', help='The directory which contains the model code.')
    parser.add_argument('output', help='The directory to output the generated code. If this directory is not empty and the -f flag is not specified, nothing will happen.')
    parser.add_argument('--force', '-f', help='Overwrite files in the output directory', action='store_true')
    args = parser.parse_args()

    return args


def validate_user_input(args):
    assert os.path.isdir(args.input), "The input directory should be a directory."

    if os.path.exists(args.output):
        assert os.path.isdir(args.output), "The output directory should be a directory."
        if not args.force:
            assert len(os.listdir(args.output)) == 0, "The output directory should be empty."


def get_input_paths(input_dir):
    contents = os.listdir(input_dir)
    input_paths = [os.path.join(os.path.dirname(input_dir), input_file) for input_file in contents]

    return filter(os.path.isfile, input_paths)


def serializable_classes(input_dir):
    for path in get_input_paths(input_dir):
        try:
            output_class = parse_model.generate_serializable_class(path)
            yield path, output_class
        except Exception as e:
            log.error("Couldn't convert {} because {} 😭".format(path, e))


def store_input(path, klass):
    with open(path, 'w') as input_file:
        input_file.write(klass)


def main():
    args = get_args()
    validate_user_input(args)
    serializable_class_output = serializable_classes(args.input)

    for path, klass in serializable_class_output:
        full_path = os.path.join(args.output, os.path.basename(path))
        log.info("Converted {} and saved to {} 😼".format(path, full_path))
        store_input(full_path, klass)


if __name__ == '__main__':
    main()
