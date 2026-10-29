# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp==1.30.0"]
# ///
"""Real MCP integration test. Creates only synthetic footage in a new directory."""
import asyncio
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BINARY = Path.home() / ".local/opt/filmcraft/bin/filmcraft-cli"
TICKS = 254016000000


def run(*args):
    return subprocess.check_output(args, stderr=subprocess.PIPE, timeout=120)


async def main():
    out = Path(tempfile.mkdtemp(prefix="filmcraft-mcp-"))
    source = out / "base.mp4"
    run("ffmpeg", "-v", "error", "-n", "-f", "lavfi", "-i",
        "testsrc2=size=320x180:rate=24:duration=4", "-f", "lavfi", "-i",
        "sine=frequency=440:sample_rate=48000:duration=4", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(source))
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    calls = []
    async with stdio_client(StdioServerParameters(command=str(BINARY), args=["mcp"])) as (r, w):
        async with ClientSession(r, w) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert {"command_run", "media_import", "render_preview", "sequence_inspect"} <= names

            async def call(name, **args):
                result = await session.call_tool(name, args)
                assert not result.isError, result
                text = "\n".join(c.text for c in result.content if c.type == "text")
                payload = json.loads(text) if text else {}
                calls.append({"tool": name, "arguments": args, "result": payload})
                return payload

            async def cmd(command, **params):
                return await call("command_run", id=command, params=params)

            await cmd("file.newProject", name="Prueba MCP de video")
            await cmd("file.newSequence", name="Corte y montaje", width=320, height=180, fps=24)
            imported = await call("media_import", paths=[str(source)])
            assert not imported["errors"]
            item = imported["items"][0]
            # Keep source 1..3 seconds, then append source 0..1: 3 seconds total.
            await cmd("timeline.place", item=item, track="V1", seconds=0,
                               sourceIn=TICKS, duration=2*TICKS)
            await cmd("timeline.place", item=item, track="V1", seconds=2,
                      sourceIn=0, duration=TICKS)
            sequence = await call("sequence_inspect")
            clips = sequence["video"][0]["items"]
            assert len(clips) == 2, sequence
            assert sequence["durationFrames"] == 72, sequence
            # A real razor cut, followed by undo, verifies both operations.
            await cmd("timeline.razor", time=TICKS, track="V1")
            cut = await call("sequence_inspect")
            assert len(cut["video"][0]["items"]) == 3
            await cmd("edit.undo")
            sequence = await call("sequence_inspect")
            assert len(sequence["video"][0]["items"]) == 2
            (out / "sequence.json").write_text(json.dumps(sequence, indent=2))
            # A title on the second video track, with audio from the base retained.
            await cmd("graphics.newText", text="Prueba MCP", position=[20, 50],
                      size=24, seconds=3, track=1, time=0, newClip=True)
            frame = await session.call_tool("render_preview", {"seconds": 0.5, "max_side": 320})
            assert not frame.isError, frame
            images = [c for c in frame.content if c.type == "image"]
            assert images, "MCP must return an image the AI can see"
            (out / "preview.png").write_bytes(base64.b64decode(images[0].data))
            await cmd("file.saveAs", path=str(out / "edicion.fcproj"))
            exported = await cmd("file.exportMedia", path=str(out / "edicion.mp4"),
                                 format="h264", audio=True, wait=True)
            assert not exported.get("offlineMedia"), exported
            await cmd("file.open", path=str(out / "edicion.fcproj"))
            reopened = await call("sequence_inspect")
            assert reopened["durationFrames"] == 72

    probe = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format",
                          "-of", "json", str(out / "edicion.mp4")))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    assert (video["width"], video["height"]) == (320, 180)
    assert video["codec_name"] == "h264" and audio["codec_name"] == "aac"
    assert abs(float(probe["format"]["duration"]) - 3) < 0.1
    assert int(video["nb_frames"]) == 72
    run("ffmpeg", "-v", "error", "-xerror", "-i", str(out / "edicion.mp4"), "-f", "null", "-")
    # Check audio contains signal, rather than just an empty audio stream.
    import array
    samples = array.array("f", run("ffmpeg", "-v", "error", "-i", str(out / "edicion.mp4"),
                                   "-vn", "-f", "f32le", "-ac", "1", "-"))
    assert samples and max(abs(s) for s in samples) > 0.01
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    report = {"status": "passed", "server": init.serverInfo.model_dump(), "tools": sorted(names),
              "checks": ["initialize", "tools/list", "import", "source in/out", "join", "razor",
                         "undo", "title", "MCP image preview", "save/reopen", "H264/AAC export",
                         "72 frames / 3 seconds", "decode without errors", "audio signal",
                         "source SHA256 unchanged"], "source_sha256": original_hash,
              "probe": probe, "calls": calls}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"status": "passed", "artifacts": str(out), "checks": report["checks"]}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
