#!/usr/bin/env python3

import asyncio
import logging
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from playwright.async_api import async_playwright
from typing import Any, Sequence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("playwright-tools")

server = Server("playwright-tools")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="scrape_page",
            description="Scrape content from a web page using Playwright",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to scrape"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector to extract specific content"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Optional selector to wait for before scraping"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="take_screenshot",
            description="Take a screenshot of a web page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to screenshot"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Whether to capture the full page",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if not arguments:
        arguments = {}
    
    if name == "scrape_page":
        return await scrape_page(arguments)
    elif name == "take_screenshot":
        return await take_screenshot(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def scrape_page(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Scrape content from a web page"""
    url = arguments.get("url")
    selector = arguments.get("selector")
    wait_for = arguments.get("wait_for")
    
    if not url:
        raise ValueError("URL is required")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url)
            
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=10000)
            
            if selector:
                content = await page.locator(selector).text_content()
            else:
                content = await page.content()
            
            await browser.close()
            
            return [types.TextContent(
                type="text",
                text=f"Content from {url}:\n\n{content}"
            )]
            
        except Exception as e:
            await browser.close()
            raise ValueError(f"Error scraping page: {str(e)}")

async def take_screenshot(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Take a screenshot of a web page"""
    url = arguments.get("url")
    full_page = arguments.get("full_page", False)
    
    if not url:
        raise ValueError("URL is required")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url)
            screenshot = await page.screenshot(full_page=full_page)
            await browser.close()
            
            return [types.TextContent(
                type="text", 
                text=f"Screenshot taken of {url} (full_page={full_page})"
            )]
            
        except Exception as e:
            await browser.close()
            raise ValueError(f"Error taking screenshot: {str(e)}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="playwright-tools",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())