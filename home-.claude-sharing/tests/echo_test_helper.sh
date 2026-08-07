#!/bin/bash
# echo_test_helper.sh -- stand-in for the real `claude` invocation in
# launch_claude_session(). Prints its argv[1] verbatim so a human can
# confirm the terminal emulator passed a multi-word, quote-containing
# argument through unchanged, then stays open long enough to read it.

echo "Received argv[1] (should match the test prompt exactly):"
echo "---"
echo "$1"
echo "---"
echo "(window stays open 8 seconds)"
sleep 8
