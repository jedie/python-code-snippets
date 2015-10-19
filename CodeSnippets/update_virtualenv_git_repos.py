#!/usr/bin/env python3

"""
    Update all git repositories in a virtualenv.

    copyleft by Jens Diemer
    release under GPL v3+
"""

import subprocess
import os
import sys
import re

try:
    import click
except ImportError as err:
    print("Error: %s" % err)
    print("Please install click!")
    sys.exit(-1)


def verbose_check_output(*args, **kwargs):
    """ 'verbose' version of subprocess.check_output() """
    verbose=kwargs.pop("verbose", False)
    if verbose:
        click.echo(click.style("\tcall: %s" % " ".join(args), fg="blue"))
    kwargs["universal_newlines"]=True
    kwargs["stderr"]=subprocess.STDOUT
    try:
        output = subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as err:
        print("\n***ERROR:")
        print(err.output)
        raise
    if verbose:
        click.echo(click.style("output:\n%s" % output, fg="blue"))
    return output


def verbose_call(*args, **kwargs):
    click.echo(
        "".join([
            "\n",
            click.style("%s $ " % kwargs.get("cwd", "."), fg="white"),
            click.style(" ".join(args), fg="blue", bold=True),
        ])
    )
    returncode = subprocess.call(args, **kwargs)
    if returncode==0:
        color="green"
    else:
        color="red"
    click.echo(click.style("(return code: %s)" % returncode, fg=color))
    return returncode

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


REXP = re.compile(r"^\*\s*(.*)$", re.MULTILINE)
def get_git_branch(path, verbose=False):
    output = verbose_check_output(
        "git", "branch", "--no-color",
        cwd=path,
        verbose=verbose
    )
    branch = REXP.findall(output)
    if len(branch)!=1:
        print("Error finding git branch from output:")
        print(output)
        print("-"*79)
        return None
    return branch[0]




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
    click.clear() # clear screen

    click.echo("Update %r..." % path)
    src_path = os.path.join(path, "src")
    if not os.path.isdir(src_path):
        click.echo("Error: Path not found: %r" % src_path)

    activate_file = os.path.join(path, "bin", "activate_this.py")
    if not os.path.isfile(activate_file):
        click.echo("Error: File not found: %r" % activate_file)

    print("Activate env with: %r" % activate_file)
    with open(activate_file, "rb") as f:
        content = f.read()
    exec(compile(content, activate_file, 'exec'), {"__file__":activate_file})
    print("sys.real_prefix:", sys.real_prefix)
    print("sys.prefix:", sys.prefix)

    click.secho("Update pip:", bold=True)
    verbose_call("pip", "install", "--upgrade", "pip", cwd=src_path)
    click.secho("Update setuptools:", bold=True)
    verbose_call("pip", "install", "--upgrade", "setuptools", cwd=src_path)

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

        pull_args = ["git", "pull"]
        branch = get_git_branch(
            abs_path,
            # verbose=True
        )
        if branch:
            # FIXME: How to removed hardcoded 'origin'?
            pull_args += ["origin", branch]

        verbose_call(*pull_args, cwd=abs_path)

        verbose_call("pip", "install", "-e", ".", "--no-deps", cwd=abs_path)


if __name__ == "__main__":
    update_env()
    click.echo("\nBye\n")

    # print(
    #     get_git_branch(
    #         os.path.expanduser("~/PyLucid_env/src/pylucid"),
    #         verbose=True
    #     )
    # )

