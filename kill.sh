#!/usr/bin/env bash
kill -9 `jobs -l | sed "s/\[.\]...\([0-9]*\).*/\1/g"`
