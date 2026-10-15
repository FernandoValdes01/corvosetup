---
name: drawio-edit
description: Edit an existing draw.io diagram. Use when the user asks to modify, update, repair, rearrange, or add/remove content in an existing `.drawio` file or draw.io XML file. Use the general draw.io skill for diagrams created from scratch.
---

# Edit existing draw.io diagrams

Use this skill for changes to an existing native draw.io file. Keep the source editable and preserve pages and content the user did not ask to change.

## Edit with the MCP

When the draw.io MCP tools are available in this Codex session, use them to inspect and change the local file:

1. Call `mcp__drawio__list_pages` with the absolute file path. Select the target page by its listed name or ID. Page indexes are zero-based.
2. Call `mcp__drawio__get_page` for each page that needs changes. It returns the page's decompressed mxGraphModel XML.
3. Edit that model while retaining unrelated cells, connections, IDs, styles, and page settings. Avoid rebuilding the page from scratch for a local change.
4. Call `mcp__drawio__set_page` with the same file path, page identifier, and the complete updated `<mxGraphModel>...</mxGraphModel>`. Do not pass a `<diagram>` wrapper. The MCP preserves other pages and matches the page's original compression format.
5. Re-list the pages and read back the changed page to confirm the intended content was saved.

Use `mcp__drawio__search_shapes` when the request needs a specific branded or industry stencil. Use its returned style and dimensions. Simple flowcharts and UML diagrams can use standard shapes without a search.

The MCP's `open_drawio_xml`, `open_drawio_mermaid`, and `open_drawio_csv` tools open a browser diagram from supplied content. They do not modify the local source file. Do not use them as a substitute for `set_page` when editing an existing file.

If the MCP tools are unavailable, edit the native mxGraph XML carefully and retain all untouched pages and metadata. Do not claim an MCP edit was made. If the requested operation cannot be done safely with the available tools, explain the limitation before replacing the file structure.

## Use draw.io Desktop when it helps

Find the installed CLI with `command -v drawio`. On this machine it is at `@HOME@/.local/bin/drawio`.

- Open the edited file in Desktop when the user asks to view it or a visual review will help: `drawio /absolute/path/to/file.drawio`.
- Apply an ELK layout only when the user asks to rearrange the diagram or the requested change needs a layout pass. Examples include `--layout verticalFlow`, `horizontalFlow`, `verticalTree`, `horizontalTree`, or `organic`. Do not relayout a carefully positioned diagram for an unrelated edit.
- Export only when requested. For example: `drawio -x -f png -e -b 10 -o /absolute/path/output.drawio.png /absolute/path/source.drawio`. Use `svg` or `pdf` in place of `png` when requested. Keep the edited source `.drawio` file.

Use the language the user chose for labels. In the final response, state the path changed and any requested export created.
