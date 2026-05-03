# -*- coding: utf-8 -*-
from __future__ import print_function
from inspect import getfullargspec

import json
import os
import sys
from time import sleep
import logging
import argparse
from .scan import LGTVScan
from .remote import LGTVRemote
from .auth import LGTVAuth
from .cursor import LGTVCursor


config_paths = [
    "/etc/lgtv/config.json",
    os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "lgtv/config.json"),
    os.path.expanduser("~/.lgtv/config.json"),
    "/opt/venvs/lgtv/config/config.json"
]

def get_commands():
    text = 'commands\n'
    commands = LGTVRemote.getCommands()
    for c in commands:
        args = getfullargspec(LGTVRemote.__dict__[c])
        line = ' ' + c
        if len(args.args) > 2:
            a = ' <' + '> <'.join(args.args[1:-1]) + '>'
            line += a
        text += line + '\n'
    return text


def parseargs(command, argv):
    args = getfullargspec(LGTVRemote.__dict__[command])
    args = args.args[1:-1]

    if len(args) != len(argv):
        raise Exception("Argument lengths do not match")

    output = {}
    for (i, a) in enumerate(args):
        if argv[i].lower() == "true":
            argv[i] = True
        elif argv[i].lower() == "false":
            argv[i] = False
        try:
            if command != "setTVChannel":
                f = int(argv[i])
                argv[i] = f
        except:
            try:
                f = float(argv[i])
                argv[i] = f
            except:
                pass
        output[a] = argv[i]
    return output


def find_config() -> str:
    for f in config_paths:
        if os.path.isfile(f):
            return f
    # no config file exists yet
    for f in config_paths:
        d = os.path.dirname(f)
        if os.path.exists(d) and os.access(d, os.W_OK):
            return f
    # no config dir exists yet
    for f in config_paths:
        d = os.path.dirname(f)
        dd = os.path.dirname(d)
        if os.path.exists(dd) and os.access(dd, os.W_OK):
            return f
    print("Cannot find suitable config path to write, create one in {}".format(" or ".join(config_paths)))
    raise Exception("No config file")

def write_config(filename: str, config):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(config, f)


def find_tv_by_scan(name, mac=None):
    logging.info(f"Scanning network for TV: {name}")
    results = LGTVScan()
    
    for tv in results:
        # Try to match by name first, then by MAC if available
        if tv.get('tv_name') == name:
            logging.info(f"Found TV '{name}' at new IP: {tv['address']}")
            return tv['address']
        # Could also match by MAC if we stored it and it's in scan results
    
    logging.warning(f"Could not find TV '{name}' on network")
    return None


def update_config_ip(filename, config, name, new_ip):
    """Update the IP address for a TV in the config"""
    if name in config:
        old_ip = config[name].get('ip', 'unknown')
        config[name]['ip'] = new_ip
        write_config(filename, config)
        logging.info(f"Updated IP for '{name}' from {old_ip} to {new_ip} in {filename}")
        return True
    return False


def execute_with_retry(ws_class, name, config_entry, ssl, command, kwargs=None, args_list=None, max_retries=1):
    for attempt in range(max_retries + 1):
        try:
            if ws_class == LGTVCursor:
                cursor = ws_class(name, **config_entry, ssl=ssl)
                cursor.connect()
                cursor.execute(args_list)
                return cursor
            else:
                ws = ws_class(name, **config_entry, ssl=ssl)
                
                if command == "on":
                    # "on" is special, it doesn't use a websocket connection
                    ws.on()
                    return ws
                
                ws.connect()
                ws.execute(command, kwargs)
                ws.run_forever()
                return ws
                
        except (ConnectionRefusedError, OSError, Exception) as e:
            error_msg = str(e)
            logging.warning(f"Connection attempt {attempt + 1} failed: {error_msg}")
            
            # Check if this looks like a connection error that might be due to wrong IP
            if attempt < max_retries and ("Connection refused" in error_msg or 
                                          "timed out" in error_msg or
                                          "Network is unreachable" in error_msg or
                                          "getaddrinfo failed" in error_msg):
                # Try to find the TV on the network
                new_ip = find_tv_by_scan(name, config_entry.get('mac'))
                
                if new_ip and new_ip != config_entry.get('ip'):
                    # Update the config with new IP
                    config_entry['ip'] = new_ip
                    # Note: We update config_entry in place, caller should save to file
                    logging.info(f"Retrying with new IP: {new_ip}")
                    continue
                else:
                    logging.error("Could not find TV on network or IP unchanged")
                    raise
            else:
                # Either out of retries or error doesn't look like IP issue
                raise
    
    return None


def main():
    parser = argparse.ArgumentParser(
        'lgtv',
        description = '''LGTV Controller\nAuthor: Karl Lattimer <karl@qdh.org.uk>''',
        epilog = get_commands(),
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--name', '-n', default=None)
    parser.add_argument('command')
    parser.add_argument('args', nargs='*')
    parser.add_argument('--no-ssl', action='store_true', help='disable SSL/TLS (use ws:// instead of wss://)')
    parser.add_argument('--debug', '-d', action='store_true', help='enable debug output')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    # SSL is enabled by default, unless --no-ssl is specified
    use_ssl = not args.no_ssl

    config = {}

    filename = find_config()
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            config = json.load(f)

    if args.command == "scan":
        # Scan doesn't use SSL (it's SSDP discovery)
        results = LGTVScan()
        if len(results) > 0:
            print(json.dumps({
                "result": "ok",
                "count": len(results),
                "list": results
            }))
            sys.exit(0)
        else:
            print(json.dumps({
                "result": "failed",
                "count": len(results)
            }))
            sys.exit(1)

    elif args.command == "auth":
        if len(args.args) != 2:
            print('lgtv auth <host> <tv_name>')
            sys.exit(1)
        host, name = args.args
        # For auth, use SSL based on flag (default is SSL enabled)
        ws = LGTVAuth(name, host, ssl=use_ssl)
        ws.connect()
        ws.run_forever()
        sleep(1)
        config[name] = ws.serialise()
        write_config(filename, config)
        print(f"Wrote config file {filename}")
        sys.exit(0)

    elif args.command == "setDefault":
        name = args.args[0]
        if filename is None:
            print("No config file found")
            sys.exit(1)
        if name not in config:
            print("TV not found in config")
            sys.exit(1)
        config["_default"] = name
        write_config(filename, config)
        print(f"Wrote default to config file {filename}")

    # These commands require a TV name and config
    else:
        try:
            kwargs = parseargs(args.command, args.args)
        except Exception:
            if args.command not in {"sendButton"}:
                parser.print_help()
                sys.exit(1)

        if args.name:
            name = args.name
        elif "_default" in config:
            name = config["_default"]
        else:
            print("A TV name is required. Set one with -n/--name or the setDefault command.")
            sys.exit(1)

        if name not in config:
            print(f"No entry with the name '{name}' was found in the configuration at {filename}.")
            sys.exit(1)

        config_entry = config[name].copy()
        config_changed = False

        if args.command == "sendButton":
            try:
                result = execute_with_retry(
                    LGTVCursor, 
                    name, 
                    config_entry, 
                    use_ssl, 
                    None, 
                    None, 
                    args.args,
                    max_retries=1
                )
                
                # If IP was updated during retry, save it
                if config_entry['ip'] != config[name]['ip']:
                    config[name]['ip'] = config_entry['ip']
                    write_config(filename, config)
                    print(f"Updated IP for '{name}' in config file")
                    
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
            return

        try:
            result = execute_with_retry(
                LGTVRemote,
                name,
                config_entry,
                use_ssl,
                args.command,
                kwargs,
                None,
                max_retries=1
            )
            
            # If IP was updated during retry, save it
            if config_entry['ip'] != config[name]['ip']:
                config[name]['ip'] = config_entry['ip']
                write_config(filename, config)
                print(f"Updated IP for '{name}' in config file")
                
        except KeyboardInterrupt:
            if result:
                result.close()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()