#!/bin/bash
# Run all tests for agent-sandboxes project

set -e  # Exit on error

echo "🧪 Running Agent Sandboxes Tests"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test CLI
echo -e "${BLUE}Testing CLI...${NC}"
cd apps/cli
uv sync --quiet
uv run pytest tests/ -v
cd ../..
echo -e "${GREEN}✓ CLI tests passed${NC}"
echo ""

# Test MCP
echo -e "${BLUE}Testing MCP Server...${NC}"
cd apps/mcp
uv sync --quiet
uv run pytest tests/ -v
cd ../..
echo -e "${GREEN}✓ MCP tests passed${NC}"
echo ""

# Test OBOX
echo -e "${BLUE}Testing OBOX...${NC}"
cd apps/obox
uv sync --quiet
uv run pytest tests/ -v
cd ../..
echo -e "${GREEN}✓ OBOX tests passed${NC}"
echo ""

echo "================================"
echo -e "${GREEN}✓ All tests passed!${NC}"
