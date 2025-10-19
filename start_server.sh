bash
#!/bin/bash

# Set the server port
SERVER_PORT=8080

# Set the server command
SERVER_COMMAND="python -m http.server $SERVER_PORT"

# Start the server
echo "Starting server on port $SERVER_PORT..."
$SERVER_COMMAND

# Wait for user to stop the server
read -p "Press Enter to stop the server..."