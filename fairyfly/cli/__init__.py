"""
Command Line Interface (CLI) entry point for fairyfly and fairyfly extensions.

Use this file only to add command related to fairyfly-core. For adding extra commands
from each extension see below.

Note:

    Do not import this module in your code directly unless you are extending the command
    line interface. For running the commands execute them from the command line or as a
    subprocess (e.g. ``subprocess.call(['fairyfly', 'viz'])``)

Honeybee is using click (https://click.palletsprojects.com/en/7.x/) for creating the CLI.
You can extend the command line interface from inside each extension by following these
steps:

1. Create a ``cli.py`` file in your extension.
2. Import the ``main`` function from this ``fairyfly.cli``.
3. Add your commands and command groups to main using add_command method.
4. Add ``import [your-extension].cli`` to ``__init__.py`` file to the commands are added
   to the cli when the module is loaded.

The good practice is to group all your extension commands in a command group named after
the extension. This will make the commands organized under extension namespace. For
instance commands for `fairyfly-therm` will be called like
``fairyfly therm [therm-command]``.


.. code-block:: python

    import click
    from fairyfly.cli import main

    @click.group()
    def therm():
        pass

    # add commands to therm group
    @therm.command('daylight-factor')
    # ...
    def daylight_factor():
        pass


    # finally add the newly created commands to fairyfly cli
    main.add_command(therm)

    # do not forget to import this module in __init__.py otherwise it will not be added
    # to fairyfly commands.

Note:

    For extension with several commands you can use a folder structure instead
    of a single file. Refer to ``fairyfly-therm`` for an example.

"""
import click
import sys
import logging
import json

from ..config import folders
from fairyfly.cli.setconfig import set_config

_logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def main():
    pass


@main.command('config')
@click.option('--output-file', help='Optional file to output the JSON string of '
              'the config object. By default, it will be printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def config(output_file):
    """Get a JSON object with all configuration information"""
    try:
        config_dict = {
            'default_simulation_folder': folders.default_simulation_folder,
            'python_package_path': folders.python_package_path,
            'python_scripts_path': folders.python_scripts_path,
            'python_exe_path': folders.python_exe_path,
            'python_version': folders.python_version_str
        }
        output_file.write(json.dumps(config_dict, indent=4))
    except Exception as e:
        _logger.exception('Failed to retrieve configurations.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@main.command('viz')
def viz():
    """Check if fairyfly is flying!"""
    click.echo('viiiiiiiiiiiiizzzzzzzzz!')


main.add_command(set_config, name='set-config')


if __name__ == "__main__":
    main()
