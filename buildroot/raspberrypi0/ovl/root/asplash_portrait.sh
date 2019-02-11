#!/bin/sh
dd if=/root/logo_portrait.fb of=/dev/fb0 bs=1536000 count=1 > /dev/null 2>&1
