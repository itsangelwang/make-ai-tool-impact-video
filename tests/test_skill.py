import importlib.util
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


validator = module("validate_package")
check_story = module("check_story")
timeline_validator = module("audit_timeline")
deepgram_tts = module("deepgram_tts")
project_state = module("project_state")
fish_audio_tts = module("fish_audio_tts")
verify_video = module("verify_video")
build_captions = module("build_captions")
fit_timeline = module("fit_timeline_to_audio")
story_audio = module("generate_story_audio")
snapshot_version = module("snapshot_version")


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
        "coverage": {"checked_at": "2026-10-21", "existing": [{"by": "official", "url": "https://example.com/launch", "shows": "功能总览"}], "our_angle": "一个人完成一件具体任务", "decision": "make"},
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

    def test_coverage_check_is_required_and_skip_stops(self):
        item = package()
        del item["coverage"]
        self.assertTrue(any("coverage" in e for e in validator.validate(item, ledger())))
        item = package()
        item["coverage"]["decision"] = "skip"
        self.assertTrue(any("skip" in e for e in validator.validate(item, ledger())))
        item = package()
        item["coverage"]["existing"] = [{"by": "someone", "url": ""}]
        self.assertTrue(any("existing 0" in e for e in validator.validate(item, ledger())))
        item = package()
        item["coverage"]["decision"] = "change-angle"
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
        self.assertEqual(preset["model"], "drama-3")
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



class SnapshotVersionTests(unittest.TestCase):
    def test_snapshots_number_up_and_skip_renders(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "script-package.json").write_text("{}")
            src = project / "video" / "src"
            (src / "components").mkdir(parents=True)
            (src / "timeline.json").write_text("{}")
            (src / "components" / "Shot.jsx").write_text("")
            (project / "video" / "renders").mkdir()
            (project / "video" / "renders" / "review-v1.mp4").write_text("")
            first, copied = snapshot_version.snapshot(project, "first review")
            second, _ = snapshot_version.snapshot(project)
            self.assertEqual((first.name, second.name), ("v1", "v2"))
            self.assertIn("video/src/timeline.json", copied)
            self.assertTrue((first / "video" / "src" / "components" / "Shot.jsx").is_file())
            self.assertFalse(any(p.suffix == ".mp4" for p in first.rglob("*")))
            self.assertEqual((first / "NOTE.txt").read_text().strip(), "first review")


class VerifyVideoToolTests(unittest.TestCase):
    def test_falls_back_to_remotion_bundled_ffmpeg(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            compositor = project / "node_modules" / "@remotion" / "compositor-test"
            compositor.mkdir(parents=True)
            for name in ("ffmpeg", "ffprobe"):
                (compositor / name).write_text("")
            video = project / "renders" / "final.mp4"
            video.parent.mkdir()
            with unittest.mock.patch.object(verify_video.shutil, "which", return_value=None):
                probe, mpeg, source = verify_video.find_tools(video)
            self.assertEqual(source, "remotion-bundled")
            self.assertEqual(Path(mpeg).parent, compositor.resolve())
            self.assertIn(str(compositor.resolve()), verify_video.tool_env(mpeg)["DYLD_LIBRARY_PATH"])

    def test_decode_names_encoders_for_bundled_ffmpeg(self):
        command = verify_video.decode_command("ffmpeg", Path("final.mp4"))
        self.assertEqual(command[-6:], ["-c:v", "rawvideo", "-c:a", "pcm_s16le", "-f", "null", "-"][-6:])
        self.assertIn("rawvideo", command)


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


class FitTimelineTests(unittest.TestCase):
    def timeline(self):
        return {
            "language": "en-US",
            "captions": [
                {"start_sec": 0.3, "end_sec": 3.0, "text": "Three quotes. Two hundred chairs."},
                {"start_sec": 3.2, "end_sec": 6.0, "text": "Now paste them into ChatGPT."},
                {"start_sec": 7.6, "end_sec": 10.0, "text": "It builds a calculator."},
                {"start_sec": 0, "end_sec": 0, "text": "ACEMODE. 10x Faster, Log Off Earlier.", "brand": True},
            ],
            "transitions": [{"start_sec": 6.1, "end_sec": 7.5, "label": "Hand off", "readable": True}],
        }

    def test_fits_measured_audio_and_keeps_transition_order(self):
        fitted = fit_timeline.fit(self.timeline(), [2.0, 4.5, 2.0, 3.6])
        caps, tr = fitted["captions"], fitted["transitions"][0]
        self.assertGreaterEqual(caps[1]["end_sec"] - caps[1]["start_sec"], 4.5)
        self.assertLess(caps[1]["end_sec"], tr["start_sec"])
        self.assertLess(tr["end_sec"], caps[2]["start_sec"])
        self.assertAlmostEqual(caps[3]["start_sec"], fitted["brand"]["start_sec"] + 0.1, places=2)
        self.assertLessEqual(fitted["brand"]["end_sec"] - fitted["brand"]["start_sec"], 4.0 + 1e-6)
        cue_errors = [e for e in timeline_validator.validate({**fitted, "duration_sec": 60}) if re.match(r"(caption|transition) \d", e)]
        self.assertEqual(cue_errors, [])

    def test_rejects_brand_line_longer_than_card(self):
        with self.assertRaises(ValueError):
            fit_timeline.fit(self.timeline(), [2.0, 2.0, 2.0, 4.5])

    def test_requires_one_audio_file_per_cue(self):
        with self.assertRaises(ValueError):
            fit_timeline.fit(self.timeline(), [2.0, 2.0])


class StoryAudioTests(unittest.TestCase):
    def test_music_follows_events_and_stops_on_reveal(self):
        import wave
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bgm.wav"
            story_audio.music({"drop": 1.0, "stop": 2.0, "boom": 3.2, "end": 4.0}, out)
            with wave.open(str(out)) as w:
                frames = w.readframes(w.getnframes())
                self.assertAlmostEqual(w.getnframes() / w.getframerate(), 4.0, places=2)
                rate = w.getframerate()
            silent = frames[int(2.2 * rate) * 2:int(2.8 * rate) * 2]
            self.assertEqual(set(silent), {0})

    def test_music_requires_end(self):
        with self.assertRaises(ValueError):
            story_audio.music({"drop": 1.0}, Path("unused.wav"))

    def test_sfx_set_matches_component_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            story_audio.sfx(Path(tmp))
            names = {p.stem for p in Path(tmp).glob("*.wav")}
        self.assertTrue({"key-1", "key-2", "key-3", "pop", "swish", "coin", "notify", "stamp", "uhoh", "return", "tick"} <= names)


class ReadmeTests(unittest.TestCase):
    """README states user-facing defaults; it must change when they change."""

    MODEL_NAMES = {"drama-3": "Drama 3", "s2.1-pro": "s2.1-pro", "s2-pro": "s2-pro", "s1": "s1"}

    def setUp(self):
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_default_voice_matches_preset(self):
        preset = fish_audio_tts.PRESETS["en-sawyer"]
        self.assertIn("Sawyer", self.readme)
        self.assertIn(self.MODEL_NAMES[preset["model"]], self.readme)

    def test_duration_matches_limits(self):
        limits = json.loads((ROOT / "scripts" / "limits.json").read_text())["duration_sec"]
        self.assertIn(f"{limits['min']}–{limits['max']} 秒", self.readme)
        self.assertIn(f"最长 {limits['extended_max']} 秒", self.readme)

    def test_default_brand_and_key_location(self):
        brand = (ROOT / "references" / "brand-system.md").read_text(encoding="utf-8")
        self.assertIn("`ACEMODE` (default)", brand)
        self.assertIn("ACEMODE", self.readme)
        self.assertIn(str(fish_audio_tts.DEFAULT_ENV_FILE), self.readme)

    def test_social_titles_are_a_stated_output(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("social-titles.md", skill)
        self.assertIn("social-titles.md", self.readme)


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


class StoryBeatTests(unittest.TestCase):
    TEMPLATE = ROOT / "assets" / "remotion-template"

    def story(self):
        return json.loads((self.TEMPLATE / "src" / "story.json").read_text(encoding="utf-8"))

    def test_template_story_uses_every_beat_and_passes(self):
        story = self.story()
        keys = {key for scene in story["scenes"] for key in scene}
        self.assertTrue({"new_feature", "shot", "roles", "checks", "access", "flow", "fix"} <= keys)
        self.assertEqual(check_story.check(story, self.TEMPLATE / "public", check_story.icon_names()), [])

    def test_beat_mistakes_are_reported(self):
        story = self.story()
        scene = next(s for s in story["scenes"] if "shot" in s)
        scene["shot"]["src"] = "assets/missing.png"
        scene["shot"]["click"]["at_sec"] = 99
        scene["roles"]["you"]["icon"] = "rocket"
        errors = check_story.check(story, self.TEMPLATE / "public", check_story.icon_names())
        self.assertTrue(any("not found" in e for e in errors))
        self.assertTrue(any("click.at_sec" in e for e in errors))
        self.assertTrue(any("rocket" in e for e in errors))

    def test_reading_load_and_static_screens_are_flagged(self):
        story = self.story()
        scene = next(s for s in story["scenes"] if s["id"] == "s2")
        scene["headline"] = "A very long headline that keeps going and asks the viewer to read far too much text"
        scene["flow"] = scene["flow"][:2]
        errors = check_story.check(story, self.TEMPLATE / "public", check_story.icon_names())
        self.assertTrue(any("words on screen" in e for e in errors))
        self.assertTrue(any("unchanged for" in e for e in errors))

    def test_neighboring_scenes_with_the_same_form_are_listed(self):
        story = self.story()
        story["scenes"][4]["flow"], story["scenes"][5]["flow"] = story["scenes"][6]["flow"], story["scenes"][6]["flow"]
        story["scenes"][5].pop("fix"); story["scenes"][5].pop("checks", None)
        story["scenes"][6].pop("access")
        self.assertTrue(check_story.variety_notes(story))

    def test_before_to_after_needs_a_chapter_transition(self):
        story = self.story()
        story["scenes"][1]["type"], story["scenes"][2]["type"] = "before-workflow", "ai-handoff"
        story["transitions"] = []
        self.assertTrue(any("chapter transition" in e for e in check_story.transition_errors(story)))
        boundary = story["scenes"][2]["start_sec"]
        story["transitions"] = [{"start_sec": boundary - 1.4, "end_sec": boundary, "label": "Hand it over", "symbol": "→", "color": "#6857F5"}]
        self.assertEqual(check_story.transition_errors(story), [])

    def test_icon_names_match_component(self):
        self.assertTrue({"doc", "table", "user", "calendar", "slides"} <= check_story.icon_names())
