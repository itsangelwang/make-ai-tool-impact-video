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
fish_audio_tts = module("fish_audio_tts")
verify_video = module("verify_video")
build_captions = module("build_captions")


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

    def test_duration_exception_allows_up_to_75_seconds(self):
        item = package()
        item["scenes"][-1]["end_sec"] = 70
        self.assertEqual(validator.validate(item, ledger(), "verified import flow needs stable holds"), [])
        item["scenes"][-1]["end_sec"] = 80
        self.assertTrue(any("55-75" in e for e in validator.validate(item, ledger(), "too long")))

    def test_brand_card_counts_toward_duration(self):
        item = package()
        item["scenes"][-1]["end_sec"] = 56.5
        item["brand"] = {"name": "ACEMODE", "slogan": "10x Faster, Log Off Earlier.", "start_sec": 56.5, "end_sec": 60}
        self.assertEqual(validator.validate(item, ledger()), [])
        item["brand"]["start_sec"] = 57
        self.assertTrue(any("brand card must start" in e for e in validator.validate(item, ledger())))

    def test_caption_length_limit_depends_on_language(self):
        english = {"language": "en-US", "text": "Tomorrow's project meeting needs one clear prep brief"}
        self.assertFalse(verify_video.caption_too_long(english))
        english["text"] = " ".join(["word"] * 15)
        self.assertTrue(verify_video.caption_too_long(english))
        self.assertTrue(verify_video.caption_too_long({"language": "zh-CN", "text": "长" * 35}))

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

    def test_fish_key_rejects_config_injection(self):
        old = os.environ.get("FISH_AUDIO_API_KEY")
        os.environ["FISH_AUDIO_API_KEY"] = "valid-looking-fish-key-123456\nheader=injected"
        try:
            with self.assertRaises(RuntimeError):
                fish_audio_tts.secret_from_environment()
        finally:
            if old is None:
                os.environ.pop("FISH_AUDIO_API_KEY", None)
            else:
                os.environ["FISH_AUDIO_API_KEY"] = old

    def test_deepgram_key_rejects_header_injection(self):
        old = os.environ.get("DEEPGRAM_API_KEY")
        os.environ["DEEPGRAM_API_KEY"] = "valid-looking-deepgram-key-1234\nX-Injected: 1"
        try:
            with self.assertRaises(RuntimeError):
                deepgram_tts.api_key_from_environment()
        finally:
            if old is None:
                os.environ.pop("DEEPGRAM_API_KEY", None)
            else:
                os.environ["DEEPGRAM_API_KEY"] = old

    def test_fish_default_env_file_is_outside_skill(self):
        self.assertEqual(fish_audio_tts.DEFAULT_ENV_FILE.parts[0], "~")

    def test_fish_preset_supplies_voice_and_flags_override(self):
        def dry_run(*extra):
            result = subprocess.run([sys.executable, ROOT / "scripts" / "fish_audio_tts.py", "--text", "[excited] Hi.", "--output", "unused.mp3", "--env-file", "/nonexistent", "--dry-run", *extra], capture_output=True, text=True)
            return json.loads(result.stdout)
        preset = dry_run("--preset", "en-sawyer")
        self.assertTrue(preset["ok"] and preset["reference_id_present"])
        self.assertEqual(preset["model"], "s2.1-pro")
        self.assertEqual(dry_run("--preset", "en-sawyer", "--model", "s2-pro")["model"], "s2-pro")
        self.assertIn("drama-3", fish_audio_tts.MODELS)

    def test_fish_env_loads_without_overriding_existing_values(self):
        old_key = os.environ.get("FISH_AUDIO_API_KEY")
        old_voice = os.environ.get("FISH_AUDIO_REFERENCE_ID")
        os.environ["FISH_AUDIO_API_KEY"] = "existing-key-value-1234567890"
        os.environ.pop("FISH_AUDIO_REFERENCE_ID", None)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                env_file = Path(tmp) / ".env"
                env_file.write_text(
                    "FISH_AUDIO_API_KEY=file-key-value-1234567890\n"
                    "FISH_AUDIO_REFERENCE_ID=voice_12345678\n"
                )
                fish_audio_tts.load_env(env_file)
            self.assertEqual(os.environ["FISH_AUDIO_API_KEY"], "existing-key-value-1234567890")
            self.assertEqual(os.environ["FISH_AUDIO_REFERENCE_ID"], "voice_12345678")
        finally:
            if old_key is None:
                os.environ.pop("FISH_AUDIO_API_KEY", None)
            else:
                os.environ["FISH_AUDIO_API_KEY"] = old_key
            if old_voice is None:
                os.environ.pop("FISH_AUDIO_REFERENCE_ID", None)
            else:
                os.environ["FISH_AUDIO_REFERENCE_ID"] = old_voice

    def test_fish_dry_run_needs_no_api_key_and_writes_no_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sample.mp3"
            env = os.environ.copy()
            env.pop("FISH_AUDIO_API_KEY", None)
            result = subprocess.run(
                [
                    sys.executable,
                    ROOT / "scripts" / "fish_audio_tts.py",
                    "--text",
                    "A short voice test.",
                    "--output",
                    output,
                    "--reference-id",
                    "voice_12345678",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(output.exists())

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
            "language": "zh-CN",
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
            "language": "zh-CN",
            "duration_sec": 60,
            "captions": [{"start_sec": 0, "end_sec": 5, "text": "你" * 50}],
            "transitions": [{"start_sec": 4, "end_sec": 5, "readable": True}],
        }
        errors = timeline_validator.validate(data)
        self.assertTrue(any("too fast" in error for error in errors))
        self.assertTrue(any("overlaps" in error for error in errors))
        self.assertTrue(any("at least 1.2" in error for error in errors))

    def test_timeline_defaults_to_english(self):
        data = {
            "duration_sec": 60,
            "captions": [{"start_sec": 0, "end_sec": 5, "text": " ".join(["word"] * 20)}],
        }
        self.assertTrue(any("words/s" in error for error in timeline_validator.validate(data)))

    def test_timeline_voice_may_add_tags_but_not_words(self):
        data = {
            "language": "en-US",
            "duration_sec": 60,
            "captions": [
                {"start_sec": 0, "end_sec": 25, "text": " ".join(["work"] * 55), "voice": "[excited] " + " ".join(["work"] * 55)},
                {"start_sec": 26.5, "end_sec": 58, "text": " ".join(["check"] * 55), "voice": "[calm] boom " + " ".join(["check"] * 55)},
            ],
        }
        errors = timeline_validator.validate(data)
        self.assertEqual(errors, ["caption 1 voice must match its text apart from [tags]"])

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



class ExampleTests(unittest.TestCase):
    """Every folder in examples/ must pass all validators."""

    def test_examples_pass_validators(self):
        folders = sorted(path for path in (ROOT / "examples").iterdir() if path.is_dir())
        self.assertGreaterEqual(len(folders), 2)
        for folder in folders:
            with self.subTest(example=folder.name):
                package_data = json.loads((folder / "script-package.json").read_text(encoding="utf-8"))
                ledger_data = json.loads((folder / "claim-ledger.json").read_text(encoding="utf-8"))
                self.assertEqual(validator.validate(package_data, ledger_data), [])
                timeline_data = json.loads((folder / "timeline.json").read_text(encoding="utf-8"))
                self.assertEqual(timeline_validator.validate(timeline_data), [])
                result = subprocess.run([sys.executable, ROOT / "scripts" / "validate_sources.py", folder / "source-ledger.json"], capture_output=True)
                self.assertEqual(result.returncode, 0)
                for cue in timeline_data["captions"]:
                    self.assertFalse(verify_video.caption_too_long({**cue, "language": timeline_data["language"]}))


class BuildCaptionsTests(unittest.TestCase):
    def test_examples_convert_via_cli(self):
        for name in ("en-meeting-brief", "zh-meeting-brief"):
            with self.subTest(example=name), tempfile.TemporaryDirectory() as tmp:
                folder = ROOT / "examples" / name
                timeline = json.loads((folder / "timeline.json").read_text())
                output = Path(tmp) / "captions.json"
                result = subprocess.run([sys.executable, ROOT / "scripts" / "build_captions.py", folder / "timeline.json", "--script", folder / "script-package.json", "--output", output], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), {"ok": True, "cues": len(timeline["captions"]), "output": str(output)})
                captions = json.loads(output.read_text())
                self.assertEqual(len(captions), len(timeline["captions"]))
                for source, converted in zip(timeline["captions"], captions):
                    self.assertEqual(converted, {"startMs": round(source["start_sec"] * 1000), "endMs": round(source["end_sec"] * 1000), "text": source["text"], "language": timeline["language"]})

    def test_highlights_rounding_and_normalization(self):
        timeline = {"language": "zh-CN", "captions": [{"start_sec": 0.1234, "end_sec": 1.2346, "text": "你好，世界！", "highlightCool": ["你好"], "highlightWarm": ["世界"]}]}
        result = build_captions.build_captions(timeline, {"narration": "你 好。世界\n"})
        self.assertEqual(result[0]["startMs"], 123)
        self.assertEqual(result[0]["endMs"], 1235)
        for key in ("highlightCool", "highlightWarm"):
            self.assertEqual(result[0][key], timeline["captions"][0][key])

    def test_invalid_highlights_fail_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            timeline = folder / "timeline.json"
            output = folder / "captions.json"
            output.write_text("keep")
            for key in ("highlightCool", "highlightWarm"):
                for value in ("五份旧记录", None, 1, {}, ["valid", 1]):
                    with self.subTest(key=key, value=value):
                        timeline.write_text(json.dumps({"language": "zh-CN", "captions": [
                            {"start_sec": 0, "end_sec": 1, "text": "第一条"},
                            {"start_sec": 1, "end_sec": 2, "text": "五份旧记录", key: value},
                        ]}, ensure_ascii=False))
                        result = subprocess.run([sys.executable, ROOT / "scripts" / "build_captions.py", timeline], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 1)
                        self.assertIn(f"caption 2 {key} must be a list of strings", result.stderr)
                        self.assertEqual(result.stdout, "")
                        self.assertEqual(output.read_text(), "keep")

    def test_mismatch_fails_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            timeline = folder / "timeline.json"
            script = folder / "script.json"
            output = folder / "captions.json"
            timeline.write_text(json.dumps({"language": "en-US", "captions": [{"start_sec": 0, "end_sec": 1, "text": "abc"}]}))
            output.write_text("keep")
            for narration, location in (("axc", 2), ("ab", 3), ("abcd", 4)):
                with self.subTest(narration=narration):
                    script.write_text(json.dumps({"narration": narration}))
                    result = subprocess.run([sys.executable, ROOT / "scripts" / "build_captions.py", timeline, "--script", script], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(f"narration mismatch at normalized character {location}", result.stderr)
                    self.assertEqual(output.read_text(), "keep")

    def test_invalid_timing_rejected(self):
        for start, end in ((-1, 1), (1, 1), (0, float("nan")), (True, 1), (0, 0.0001)):
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                build_captions.build_captions({"language": "en-US", "captions": [{"start_sec": start, "end_sec": end, "text": "hi"}]})


class LimitsConsistencyTests(unittest.TestCase):
    """Docs repeat key numbers for readers; they must match scripts/limits.json."""

    def docs(self):
        return {path: path.read_text(encoding="utf-8") for path in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]}

    def assert_ranges(self, pattern, expected):
        import re
        found = []
        for path, text in self.docs().items():
            for match in re.finditer(pattern, text):
                found.append((path.name, (int(match.group(1)), int(match.group(2)))))
        self.assertTrue(found, f"no matches for {pattern}")
        for name, value in found:
            self.assertEqual(value, expected, f"{name} disagrees with limits.json")

    def test_narration_ranges_match(self):
        limits = json.loads((ROOT / "scripts" / "limits.json").read_text())
        zh, en = limits["narration"]["zh"], limits["narration"]["en"]
        self.assert_ranges(r"(\d{2,3})–(\d{2,3}) Han characters", (zh["min"], zh["max"]))
        self.assert_ranges(r"(\d{2,3})–(\d{2,3}) (?:spoken English )?words(?! per)", (en["min"], en["max"]))

    def test_target_duration_matches(self):
        limits = json.loads((ROOT / "scripts" / "limits.json").read_text())["duration_sec"]
        self.assert_ranges(r"(\d{2})–(\d{2}) seconds?", (limits["min"], limits["max"]))


if __name__ == "__main__":
    unittest.main()
