#!/usr/bin/env bash
kill -9 `ps a | grep "python ./clipshare.py" | grep -v "grep" | sed "s/.\([0-9]*\).*/\1/g"`
