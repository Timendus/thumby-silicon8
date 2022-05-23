#!/bin/bash

# This sends Silicon8 to your Thumby, and launches it.
# It only sends files modified since the last send to your Tumby to save time.
# Works on Mac, depends on Ampy being installed.

TIME="send.time"
export AMPY_PORT=`ls /dev/tty.usbmodem*`

if [ -z "$AMPY_PORT" ]; then
  echo "Could not find your Thumby! Is it plugged in and turned on..?"
  exit 2
fi

function send {
  for file in $1
  do
    if [ -f $file ] && [ $file -nt $TIME ]; then
      echo "Sending file ${file:1}"
      if ! ampy put $file ${file:1}; then
        echo
        echo "Ampy gave an error. Is code.thumby.us interfering..?"
        exit 2
      fi
    fi
    if [ -d $file ]; then
      if [ $file -nt $TIME ]; then
        # Does this directory exist on the Thumby yet?
        if ! ampy ls ${file:1} > /dev/null; then
          echo "Creating directory ${file:1}"
          if ! ampy mkdir ${file:1}; then
            echo
            echo "Ampy gave an error. Is code.thumby.us interfering..?"
            exit 2
          fi
        fi
      fi
      send "$file/*"
    fi
  done
}

send "./Games/*"
touch send.time

echo "Running:"
cat send.py
ampy run send.py
