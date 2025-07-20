#!/usr/bin/env python3
"""
Playwright MCP Server - Web automation and scraping tools
"""

import asyncio
import base64
from typing import Any, Dict, List
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from playwright.async_api import async_playwright

# Initialize the MCP server
server = Server("playwright-tools")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="scrape_page",
            description="Scrape content from a web page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector to extract specific content (optional)"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "CSS selector to wait for before scraping (optional)"
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="screenshot_page",
            description="Take a screenshot of a web page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to screenshot"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Take full page screenshot",
                        "default": False
                    },
                    "width": {
                        "type": "integer",
                        "description": "Viewport width",
                        "default": 1280
                    },
                    "height": {
                        "type": "integer",
                        "description": "Viewport height",
                        "default": 720
                    }
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="fill_form",
            description="Fill and submit a form on a web page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the page with the form"
                    },
                    "form_data": {
                        "type": "object",
                        "description": "Form field selectors and values",
                        "additionalProperties": {"type": "string"}
                    },
                    "submit_selector": {
                        "type": "string",
                        "description": "CSS selector for submit button"
                    }
                },
                "required": ["url", "form_data"]
            }
        ),
        types.Tool(
            name="click_element",
            description="Click an element on a web page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the page"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector of element to click"
                    },
                    "wait_for_navigation": {
                        "type": "boolean",
                        "description": "Wait for navigation after click",
                        "default": False
                    }
                },
                "required": ["url", "selector"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            if name == "scrape_page":
                url = arguments.get("url")
                selector = arguments.get("selector")
                wait_for = arguments.get("wait_for")
                
                await page.goto(url)
                
                if wait_for:
                    await page.wait_for_selector(wait_for)
                
                if selector:
                    elements = await page.query_selector_all(selector)
                    content = []
                    for element in elements:
                        text = await element.text_content()
                        if text:
                            content.append(text.strip())
                    result = "\n".join(content)
                else:
                    result = await page.content()
                
                await browser.close()
                return [
                    types.TextContent(
                        type="text",
                        text=f"Scraped content from {url}:\n\n{result}"
                    )
                ]
            
            elif name == "screenshot_page":
                url = arguments.get("url")
                full_page = arguments.get("full_page", False)
                width = arguments.get("width", 1280)
                height = arguments.get("height", 720)
                
                await page.set_viewport_size({"width": width, "height": height})
                await page.goto(url)
                
                screenshot = await page.screenshot(full_page=full_page)
                screenshot_b64 = base64.b64encode(screenshot).decode()
                
                await browser.close()
                return [
                    types.TextContent(
                        type="text",
                        text=f"Screenshot taken of {url}\nBase64 data: {screenshot_b64[:100]}... (truncated)"
                    )
                ]
            
            elif name == "fill_form":
                url = arguments.get("url")
                form_data = arguments.get("form_data", {})
                submit_selector = arguments.get("submit_selector")
                
                await page.goto(url)
                
                for selector, value in form_data.items():
                    await page.fill(selector, value)
                
                if submit_selector:
                    await page.click(submit_selector)
                    await page.wait_for_load_state()
                
                result_url = page.url
                await browser.close()
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Form filled and submitted. Current URL: {result_url}"
                    )
                ]
            
            elif name == "click_element":
                url = arguments.get("url")
                selector = arguments.get("selector")
                wait_for_navigation = arguments.get("wait_for_navigation", False)
                
                await page.goto(url)
                
                if wait_for_navigation:
                    async with page.expect_navigation():
                        await page.click(selector)
                else:
                    await page.click(selector)
                
                result_url = page.url
                await browser.close()
                
                return [
                    types.TextContent(
                        type="text",
                        text=f"Clicked element {selector}. Current URL: {result_url}"
                    )
                ]
            
            else:
                await browser.close()
                raise ValueError(f"Unknown tool: {name}")
                
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())