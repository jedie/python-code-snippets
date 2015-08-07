#!/usr/bin/env python3

"""
    Update all git repositories in a virtualenv.

    copyleft by Jens Diemer
    release under GPL v3+
"""

import subprocess
import os
import sys

try:
    import click
except ImportError as err:
    print("Error: %s" % err)
    print("Please install click!")
    sys.exit(-1)


def verbose_call(*args, **kwargs):
    click.echo(click.style("\tcall: %s" % " ".join(args), fg="blue"))
    returncode = subprocess.call(args, **kwargs)
    if returncode==0:
        color="green"
    else:
        color="red"
    click.echo(click.style("(return code: %s)" % returncode, fg=color))
    return returncode


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("path", type=click.Path(
    exists=True,
    file_okay=False, dir_okay=True,
    writable=False, readable=True,
    resolve_path=True
))
def update_env(path):
    """
    Update a virtualenv by Jens Diemer - GPL v3
    """
    click.echo("Update %r..." % path)
    src_path = os.path.join(path, "src")
    if not os.path.isdir(src_path):
        click.echo("Error!")

    for path in os.listdir(src_path):
        abs_path = os.path.join(src_path, path)
        if not os.path.isdir(abs_path):
            continue

        git_dir = os.path.join(abs_path, ".git")
        if not os.path.isdir(git_dir):
            click.echo("Skip %r (contains no '.git' dir)" % path)
            continue

        click.echo("_"*79)
        click.echo(click.style("Update %r:" % path, bold=True))

        verbose_call("git", "fetch", "--all", cwd=abs_path)
        verbose_call("git", "pull", cwd=abs_path)


if __name__ == "__main__":
    update_env()
    click.echo("\nBye\n")
