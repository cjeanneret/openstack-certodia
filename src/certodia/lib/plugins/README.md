# Plugins

## Structure
A plugin consists in a directory and, at least, an `__init__.py` file.

It must contains a class named `Client`, and expose some mandatory methods.

It must take the following arguments in the Client constructor:
- parent_parser (for argparse)
- logger (logging.getLogger() object)

## Consistency checks and error control
All the consistency checks must be done in the plugin. If an error occurs, it must return a "False"
value. It's a good practice to, at least, log what's happening - please use the "logger" instance.

## Methods you must expose in the Client class
### config
This method must configure your plugin. It must take a "conf" object, as defined
in the `config` class present in our lib directory.

Note: this config method should take care only of the plugin specific arguments.

### fetch
This method must fetches and returns, in that order, the certificate, its chain and the private key.

Please ensure returned contents are all in a valid PEM format.

### build_parser
This method must take an argparser.sub_parser object in argument, and sets plugin dedicated parameters.

It must return the updated argument parser.

### push
This method must push objects to the storage backend


If your Client needs other methods, they must be called from the three mentioned public
methods.

Certodia must be considered as a simple skeleton, and your plugins will be the flesh and muscles.
