import argparse
import re
import sys
import yaml

def interact(script, read_from, write_to):
    while true:
        inline = read_from.read()
        for pattern, action in script:
            matched = pattern.search(inline)
            if matched:
                pass            # todo: handle action

def main():
    parser = argparse.ArgumentParser()
    # todo: arg for running a program or connecting to a tty
    # todo: maybe allow a socket pair somehow?
    parser.add_argument("script")
    args = parser.parse_args()
    with open(args.script, 'r') as script_stream:
        raw_script = yaml.load(script_stream)
    script = { re.compile(pattern) if isinstance(pattern, str) else pattern: action
               for pattern, action in raw_script }
    interact(script, read_stream, write_stream);
    return 0

if __name__ == "__main__":
    sys.exit(main())
