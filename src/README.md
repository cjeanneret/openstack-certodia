# certodia
This is the main script and its dependencies.

## Configuration file
The configuration file is a simple YAML. The key names are a 
camelized version of the CLI option name, for exemple, 
`--cust-auth-key` becomes `CustAuthKey` in the YAML.

Please refer to the script and plugins help in order to find the
parameter names.

## Plugins
A list of plugins can be displayed using `certodia.py --help`

### Add new plugin
Please check the lib/plugins/README.md in order to check how to add
new plugins for this script.
