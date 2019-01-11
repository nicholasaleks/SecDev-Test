#!/usr/bin/env bash
python AutomatedCollection.py --src / --dest /collect --target_extensions .secret .old --target_regex secret* --archive true --archive_name collect.tar.gz --upload False --clean_dest False
