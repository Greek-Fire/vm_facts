#!/usr/bin/env bash

#!/bin/bash

# Check if the SSH agent is running
agent_running=$(pgrep ssh-agent)

# Start the SSH agent if it's not running
if [ -z "$agent_running" ]; then
  echo "SSH agent is not running. Starting the agent now."
  eval "$(ssh-agent -s)"
else
  echo "SSH agent is already running (PID: $agent_running)."
fi

# Add the SSH key to the agent
ssh-add ~/.ssh/my_private_key

# Verify that the key was added
ssh-add -l

python3.6 vm_builder.py "$@"