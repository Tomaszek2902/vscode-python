from __future__ import absolute_import

import argparse
import sys

from . import pytest, report
from .errors import UnsupportedToolError, UnsupportedCommandError


# Set this to True to pretty-print the output.
DEBUG=False
#DEBUG=True

TOOLS = {
    'pytest': {
        '_add_subparser': pytest.add_cli_subparser,
        'discover': pytest.discover,
        },
    }
REPORTERS = {
    'discover': report.report_discovered,
    }


def parse_args(
        argv=sys.argv[1:],
        prog=sys.argv[0],
        ):
    """
    Return the subcommand & tool to run, along with its args.

    This defines the standard CLI for the different testing frameworks.
    """
    parser = argparse.ArgumentParser(
            description='Run Python testing operations.',
            prog=prog,
            )
    cmdsubs = parser.add_subparsers(dest='cmd')

    # Add "run" and "debug" subcommands when ready.
    for cmdname in ['discover']:
        sub = cmdsubs.add_parser(cmdname)
        subsubs = sub.add_subparsers(dest='tool')
        for toolname in sorted(TOOLS):
            try:
                add_subparser = TOOLS[toolname]['_add_subparser']
            except KeyError:
                continue
            add_subparser(cmdname, toolname, subsubs)

    # Parse the args!
    args, toolargs = parser.parse_known_args(argv)
    ns = vars(args)

    cmd = ns.pop('cmd')
    if not cmd:
        parser.error('missing command')
    tool = ns.pop('tool')
    if not tool:
        parser.error('missing tool')

    return tool, cmd, ns, toolargs


def main(toolname, cmdname, subargs, toolargs,
         _tools=TOOLS, _reporters=REPORTERS):
    try:
        tool = _tools[toolname]
    except KeyError:
        raise UnsupportedToolError(toolname)

    try:
        run = tool[cmdname]
        report_result = _reporters[cmdname]
    except KeyError:
        raise UnsupportedCommandError(cmdname)

    result = run(toolargs, **subargs)
    report_result(result, debug=DEBUG)


if __name__ == '__main__':
    tool, cmd, subargs, toolargs = parse_args()
    main(tool, cmd, subargs, toolargs)
