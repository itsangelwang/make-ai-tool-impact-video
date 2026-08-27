import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


validator = module("validate_package")
timeline_validator = module("audit_timeline")
deepgram_tts = module("deepgram_tts")
project_state = module("project_state")


def package(task="整理会议纪要", audience="项目经理"):
    types = ["pain-hook", "before-workflow", "ai-handoff", "after-workflow", "human-check", "next-action"]
    ends = [7, 17, 27, 39, 50, 60]
    start = 0
    scenes = []
    for i, (kind, end) in enumerate(zip(types, ends), 1):
        scenes.append({"id": f"s{i}", "type": kind, "purpose": f"说明{kind}", "start_sec": start, "end_sec": end, "headline": task, "visual": "清晰的流程变化", "claim_ids": ["c1"]})
        start = end
    return {
        "schema_version": 1,
        "language": "zh-CN",
        "market": "CN",
        "tool": {"name": "Example AI", "url": "https://example.com", "one_line_capability": "整理输入材料"},
        "audience": audience,
        "task": task,
        "before_steps": ["收集材料", "逐条整理", "人工归纳"],
        "friction": "重复搬运信息",
        "ai_change": "先生成结构化草稿",
        "after_steps": ["提交材料", "AI生成草稿", "人工核对"],
        "human_check": "核对事实和负责人",
        "readiness": "try-now",
        "next_action": "用一份非敏感材料对照测试",
        "narration": "你" * 180,
        "scenes": scenes,
    }


def ledger():
    return {"claims": [{"id": "c1", "text": "工具可以整理输入材料", "level": "vendor-claim", "source_url": "https://example.com/docs", "source_type": "official", "accessed_at": "2026-08-17", "support": "官方功能说明", "boundary": "未独立测量效率"}]}


class PackageTests(unittest.TestCase):
    def test_meeting_notes(self):
        self.assertEqual(validator.validate(package(), ledger()), [])

    def test_resume_editing(self):
        self.assertEqual(validator.validate(package("针对职位修改简历", "求职者"), ledger()), [])

    def test_trip_planning(self):
        self.assertEqual(validator.validate(package("整理旅行计划", "周末出行者"), ledger()), [])

    def test_insufficient_sources_fail(self):
        self.assertTrue(validator.validate(package(), {"claims": []}))

    def test_waitlist_is_explicit(self):
        item = package()
        item["readiness"] = "watch"
        self.assertEqual(validator.validate(item, ledger()), [])

    def test_bad_duration_fails(self):
        item = package()
        item["scenes"][-1]["end_sec"] = 70
        self.assertTrue(any("55-65" in e for e in validator.validate(item, ledger())))

    def test_english_market_package(self):
        item = package("build a meeting prep brief", "project manager")
        item["language"] = "en-US"
        item["market"] = "US"
        item["narration"] = " ".join(["work"] * 120)
        self.assertEqual(validator.validate(item, ledger()), [])

    def test_english_release_opening_fails(self):
        item = package()
        item["language"] = "en-US"
        item["market"] = "US"
        item["narration"] = "Introducing a new AI tool. " + " ".join(["work"] * 115)
        self.assertTrue(any("product release" in e for e in validator.validate(item, ledger())))


class StateAndUtilitiesTests(unittest.TestCase):
    def test_state_cannot_read_outside_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            private = root / "private.txt"
            private.write_text("private")
            state = {"review": {"files": {"package": {
                "path": "../private.txt", "sha256": project_state.digest(private)
            }}}}
            ok, changed = project_state.integrity(state, project)
            self.assertFalse(ok)
            self.assertEqual(changed, ["package"])

    def test_atomic_state_write_replaces_symlink_not_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            private = root / "private.txt"
            private.write_text("keep")
            (project / ".impact-video-state.json").symlink_to(private)
            project_state.write(project, {"stage": "draft"})
            self.assertEqual(private.read_text(), "keep")
            self.assertFalse((project / ".impact-video-state.json").is_symlink())

    def test_approval_invalidates_after_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            files = []
            for name in ("package", "claims", "story", "sources", "cover", "opening"):
                path = project / name
                path.write_text(name)
                files.extend([f"--{name}", str(path)])
            state = ROOT / "scripts" / "project_state.py"
            subprocess.run([sys.executable, state, "init", project], check=True, capture_output=True)
            subprocess.run([sys.executable, state, "review", project, *files], check=True, capture_output=True)
            subprocess.run([sys.executable, state, "approve", project, "--by", "user"], check=True, capture_output=True)
            (project / "story").write_text("changed")
            result = subprocess.run([sys.executable, state, "status", project], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("review-invalidated", result.stdout)

    def test_review_state_uses_project_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            flags = []
            for name in ("package", "claims", "story", "sources", "cover", "opening"):
                path = project / name
                path.write_text(name)
                flags.extend([f"--{name}", str(path)])
            state_script = ROOT / "scripts" / "project_state.py"
            subprocess.run([sys.executable, state_script, "init", project], check=True, capture_output=True)
            subprocess.run([sys.executable, state_script, "review", project, *flags], check=True, capture_output=True)
            state = json.loads((project / ".impact-video-state.json").read_text())
            self.assertEqual(state["review"]["files"]["package"]["path"], "package")
            self.assertNotIn(str(project), json.dumps(state))

    def test_openrouter_key_rejects_config_injection(self):
        tts_module = module("openrouter_tts")
        old = os.environ.get("OPENROUTER_API_KEY")
        os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-validvalue1234567890\nheader = injected"
        try:
            with self.assertRaises(RuntimeError):
                tts_module.api_key_from_environment()
        finally:
            if old is None:
                os.environ.pop("OPENROUTER_API_KEY", None)
            else:
                os.environ["OPENROUTER_API_KEY"] = old

    def test_caption_pipeline_covers_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            script = folder / "package.json"
            output = folder / "captions.json"
            script.write_text(json.dumps({"narration": "先整理材料。再让工具生成草稿。最后人工核对。"}, ensure_ascii=False))
            subprocess.run([sys.executable, ROOT / "scripts" / "caption_pipeline.py", "--script", script, "--duration-ms", "60000", "--output", output], check=True, capture_output=True)
            cues = json.loads(output.read_text())
            self.assertEqual(cues[0]["startMs"], 0)
            self.assertEqual(cues[-1]["endMs"], 60000)

    def test_generated_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "sources.json"
            ledger_path.write_text(json.dumps({"assets": [{"path": "fake.png", "origin": "generated", "rights": "cleared", "role": "product-evidence", "attribution": "AI", "generated": True}]}))
            result = subprocess.run([sys.executable, ROOT / "scripts" / "validate_sources.py", ledger_path], capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_timeline_accepts_speakable_captions(self):
        data = {
            "duration_sec": 60,
            "captions": [
                {"start_sec": 0, "end_sec": 30, "text": "你" * 90},
                {"start_sec": 31.5, "end_sec": 58, "text": "我" * 80},
            ],
            "transitions": [
                {"start_sec": 30, "end_sec": 31.5, "label": "下一步", "readable": True}
            ],
        }
        self.assertEqual(timeline_validator.validate(data), [])

    def test_timeline_rejects_fast_caption_and_overlap(self):
        data = {
            "duration_sec": 60,
            "captions": [{"start_sec": 0, "end_sec": 5, "text": "你" * 50}],
            "transitions": [{"start_sec": 4, "end_sec": 5, "readable": True}],
        }
        errors = timeline_validator.validate(data)
        self.assertTrue(any("too fast" in error for error in errors))
        self.assertTrue(any("overlaps" in error for error in errors))
        self.assertTrue(any("at least 1.2" in error for error in errors))

    def test_english_timeline(self):
        data = {
            "language": "en-US",
            "duration_sec": 60,
            "captions": [
                {"start_sec": 0, "end_sec": 25, "text": " ".join(["work"] * 55)},
                {"start_sec": 26.5, "end_sec": 58, "text": " ".join(["check"] * 55)},
            ],
            "transitions": [{"start_sec": 25, "end_sec": 26.5, "readable": True}],
        }
        self.assertEqual(timeline_validator.validate(data), [])

    def test_flux_url_and_key_safety(self):
        url = deepgram_tts.build_url("flux-hannah-en", 0.95, 1, "mp3")
        self.assertIn("/v2/speak?", url)
        self.assertIn("model=flux-hannah-en", url)
        self.assertNotIn("DEEPGRAM_API_KEY", url)


if __name__ == "__main__":
    unittest.main()
