# Alamoswagger
Alamoswagger adds [`ResponseObjectSerializable`](https://github.com/Alamofire/Alamofire#generic-response-object-serialization) protocol conformance to classes in the Swift model files generated with [swagger-codegen](www.github.com/swagger-api/swagger-codegen). The code is written in Python.

## Requirements
Make sure Python 3 is installed.

## Usage
Generate your Swift client models with [swagger-codegen](www.github.com/swagger-api/swagger-codegen) then run:

    $ pip install virtualenv
	$ virtualenv -p /usr/local/bin/python3 alamoswagger
    $ pip install -r requirements.txt
    $ python alamoswagger.py input_dir output_dir   # Note: if output_dir exists nothing will happen

## Tests
All the tests are specified in `docstrings`. To run them, execute `$ python -m doctest parse_model.py -v`

## Caveats
If [swagger-codegen](www.github.com/swagger-api/swagger-codegen) ever changes the format of their Swift model files, this code will probably break. Right now it works with version 2.1.6 on macOS Sierra.
