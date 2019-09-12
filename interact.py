#!/usr/bin/env python3

import argparse
import re
import shlex
import subprocess
import sys
import yaml

def perform_assignment(action,
                       received, matched,
                       variables,
                       read_from, write_to,
                       verbose=False):
    variables[matched.group(1)] = eval(matched.group(2))
    return True

def perform_shell_command(action,
                          received, matched,
                          variables,
                          read_from, write_to,
                          verbose=False):
    pass
    return True

def perform_send_shell_output(action,
                              received, matched,
                              variables,
                              read_from, write_to,
                              verbose=False):
    pass
    return True

def perform_funcall(action,
                    received, matched,
                    variables,
                    read_from, write_to,
                    verbose=False):
    fname = matched.group(1)
    if fname == "send":
        perform_send(eval(matched.group(2))+"\n",
                     received, matched,
                     variables,
                     read_from, write_to,
                     verbose)
    elif fname == "quit":
        return False
    else:
        eval(action)
    return True

def perform_send(action,
                 received, matched,
                 variables,
                 read_from, write_to,
                 verbose=False):
    if verbose:
        print("Sending", action, "to process")
    write_to.write(action)
    write_to.flush()
    return True

performers = {re.compile(pattern): action
              for pattern, action in
              {
                  "([a-z0-9_]+) = (.+)": perform_assignment,
                  "!(.+)": perform_shell_command,
                  "(.+)\|": perform_send_shell_output,
                  "([.a-z0-9_]+)\((.*)\)": perform_funcall,
                  }.items()
}

def perform(action,
            received, matched,
            variables,
            read_from, write_to,
            verbose=False):
    """Perform a single action."""
    if verbose:
        print("performing", action)
    for pattern, action in performers.items():
        do_this = pattern.search(received)
        if do_this:
            return action(action,
                          received, do_this,
                          variables,
                          read_from, write_to,
                          verbose)
    return perform_send(action,
                        received, do_this,
                        variables,
                        read_from, write_to,
                        verbose)

def handle_line(received, interactions, variables, read_from, write_to, verbose=False):
    """Handle one line of data received from the target."""
    for pattern, action in interactions.items():
        matched = pattern.search(received)
        if matched:
            match_variables = {'\\' + str(n): v
                               for n, v in enumerate(matched.groups())}
            variables.update(match_variables)
            received = received % variables
            if isinstance(action, str):
                if not perform(action,
                               received, matched,
                               variables,
                               read_from, write_to,
                               verbose):
                    running = False
            elif type(action) == list:
                for line in action:
                    if not perform(action,
                                   received, matched,
                                   variables,
                                   read_from, write_to,
                                   verbose):
                        running = False
            for mv in match_variables.keys():
                del variables[mv]
            # use only one pattern
            break

def interact(interactions, variables, read_from, write_to, verbose=False):
    """Communicate with a pair of streams using a scripted set of interactions."""
    print("interact reading from", read_from)
    print("interact writing to", write_to)
    print("interactions are", interactions)
    # this may be useful: https://eli.thegreenplace.net/2017/interacting-with-a-long-running-child-process-in-python/
    line = ""
    running = True
    line_by_line = True
    while running:
        if line_by_line:
            received = read_from.readline().decode('utf-8')
            if received == "":
                running = False
                break
            handle_line(received, interactions, variables, read_from, write_to, verbose)
        else:
            new_input = str(read_from.read())
            print("new input is", new_input)
            line += new_input
            lines = line.split('\n')
            # If the input ended with a newline, the result of split will
            # end with an empty string.  So if it doesn't, that means we
            # have a partial line to carry over to the next time.
            if len(lines[-1]) > 0:
                line = lines[-1]
                lines = lines[:-1]
            for one_line in lines:
                handle_line(one_line.decode('utf-8'), interactions, variables, read_from, write_to, verbose)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("script")
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.verbose:
        print("running verbosely")
    with open(args.script, 'r') as script_stream:
        raw_script = yaml.load(script_stream)
    target = raw_script['target']
    print("target is", target)
    if 'run' in target:
        if 'connect' in target:
            print("Only one of 'run' and 'connect' may be given in the 'target' section.")
            return 1
        command_line = shlex.split(target['run'])
        if args.verbose:
            print("Starting", command_line)
        process = subprocess.Popen(command_line,
                                   bufsize=0,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        print("process is", process)
        read_stream = process.stdout
        write_stream = process.stdin
    elif 'connect' in target:
        print("'connect' is not yet implemented")
        return 2
    else:
        print("One of 'run' or 'connect' must be given in the 'target' section")
        return 1
    variables = raw_script.get('settings', {})
    for n, elt in enumerate(args.rest):
        variables[str(n)] = elt
    interactions = { re.compile(pattern)
                     if isinstance(pattern, str)
                     else pattern: action
                     for pattern, action in raw_script['responses'].items() }
    interact(interactions, variables,
             read_stream, write_stream,
             args.verbose);
    return 0

if __name__ == "__main__":
    sys.exit(main())
