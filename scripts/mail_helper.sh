#!/bin/bash
# MCP Agent Mail Helper Script for SpendSense
# Quick commands for common mail operations

set -e

# Configuration
PROJECT_KEY="/Users/caseymanos/GauntletAI/SpendSense"
AGENT_NAME="WhiteCastle"
MCP_URL="http://127.0.0.1:8765/mcp/"
BEARER_TOKEN="1a98812da9391bfddf4f243cfe442b9cf45f44fe7923d17c4f867ee194d4c20f"

# Helper function to call MCP API
call_mcp() {
    local tool_name=$1
    local args=$2

    curl -s -X POST "${MCP_URL}" \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"${tool_name}\",\"arguments\":${args}}}" \
        | python3 -m json.tool
}

# Command functions
inbox() {
    local limit=${1:-10}
    echo "📬 Fetching inbox (limit: ${limit})..."
    call_mcp "fetch_inbox" "{\"project_key\":\"${PROJECT_KEY}\",\"agent_name\":\"${AGENT_NAME}\",\"limit\":${limit},\"include_bodies\":true}"
}

reservations() {
    echo "📁 Fetching file reservations..."
    curl -s -X POST "${MCP_URL}" \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"resources/read\",\"params\":{\"uri\":\"resource://file_reservations/users-caseymanos-gauntletai-spendsense?active_only=true\"}}" \
        | python3 -m json.tool
}

reserve() {
    local paths=$1
    local ttl=${2:-3600}
    local exclusive=${3:-false}
    local reason=$4

    if [ -z "$paths" ] || [ -z "$reason" ]; then
        echo "Usage: reserve <paths> [ttl_seconds] [exclusive] <reason>"
        echo "Example: reserve 'ingest/**' 7200 false 'Working on data generation'"
        return 1
    fi

    echo "🔒 Reserving: ${paths}"
    call_mcp "file_reservation_paths" "{\"project_key\":\"${PROJECT_KEY}\",\"agent_name\":\"${AGENT_NAME}\",\"paths\":[\"${paths}\"],\"ttl_seconds\":${ttl},\"exclusive\":${exclusive},\"reason\":\"${reason}\"}"
}

release() {
    local paths=$1

    if [ -z "$paths" ]; then
        echo "Usage: release <paths>"
        echo "Example: release 'ingest/**'"
        return 1
    fi

    echo "🔓 Releasing: ${paths}"
    call_mcp "release_file_reservations" "{\"project_key\":\"${PROJECT_KEY}\",\"agent_name\":\"${AGENT_NAME}\",\"paths\":[\"${paths}\"]}"
}

send() {
    local to=$1
    local subject=$2
    local body=$3

    if [ -z "$to" ] || [ -z "$subject" ] || [ -z "$body" ]; then
        echo "Usage: send <to_agent> <subject> <body>"
        echo "Example: send 'BlueLake' 'API Update' 'New endpoint available'"
        return 1
    fi

    echo "📤 Sending message to ${to}..."
    call_mcp "send_message" "{\"project_key\":\"${PROJECT_KEY}\",\"sender_name\":\"${AGENT_NAME}\",\"to\":[\"${to}\"],\"subject\":\"${subject}\",\"body_md\":\"${body}\"}"
}

search() {
    local query=$1
    local limit=${2:-10}

    if [ -z "$query" ]; then
        echo "Usage: search <query> [limit]"
        echo "Example: search 'API' 5"
        return 1
    fi

    echo "🔍 Searching: ${query}"
    call_mcp "search_messages" "{\"project_key\":\"${PROJECT_KEY}\",\"query\":\"${query}\",\"limit\":${limit}}"
}

whois() {
    local agent=${1:-$AGENT_NAME}

    echo "👤 Getting profile for: ${agent}"
    call_mcp "whois" "{\"project_key\":\"${PROJECT_KEY}\",\"agent_name\":\"${agent}\"}"
}

agents() {
    echo "👥 Listing all agents..."
    curl -s -X POST "${MCP_URL}" \
        -H "Authorization: Bearer ${BEARER_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"resources/read\",\"params\":{\"uri\":\"resource://project/users-caseymanos-gauntletai-spendsense\"}}" \
        | python3 -m json.tool
}

webui() {
    echo "🌐 Opening Web UI..."
    open "http://127.0.0.1:8765/mail/users-caseymanos-gauntletai-spendsense"
}

help() {
    cat <<EOF
MCP Agent Mail Helper for SpendSense

Usage: $0 <command> [args]

Commands:
  inbox [limit]                  - Fetch inbox messages (default limit: 10)
  reservations                   - List active file reservations
  reserve <paths> [ttl] [excl] <reason>  - Reserve file paths
  release <paths>                - Release file reservations
  send <to> <subject> <body>     - Send a message
  search <query> [limit]         - Search messages (default limit: 10)
  whois [agent]                  - Get agent profile (default: WhiteCastle)
  agents                         - List all agents in project
  webui                          - Open web UI in browser
  help                           - Show this help

Examples:
  $0 inbox 5
  $0 reserve 'ingest/**' 7200 false 'Working on data generation'
  $0 release 'ingest/**'
  $0 send 'BlueLake' 'API Ready' 'Feature detection API is ready'
  $0 search 'persona' 10
  $0 whois BlueLake
  $0 webui

Environment:
  PROJECT_KEY: ${PROJECT_KEY}
  AGENT_NAME: ${AGENT_NAME}
  MCP_URL: ${MCP_URL}
EOF
}

# Main command dispatcher
case "$1" in
    inbox)
        inbox "$2"
        ;;
    reservations)
        reservations
        ;;
    reserve)
        reserve "$2" "$3" "$4" "$5"
        ;;
    release)
        release "$2"
        ;;
    send)
        send "$2" "$3" "$4"
        ;;
    search)
        search "$2" "$3"
        ;;
    whois)
        whois "$2"
        ;;
    agents)
        agents
        ;;
    webui)
        webui
        ;;
    help|"")
        help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
