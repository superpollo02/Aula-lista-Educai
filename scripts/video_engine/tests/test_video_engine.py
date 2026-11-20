"""Unit tests for EducAI Video Studio engine and SCORM packager."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.video_engine.captions.capcut_ass import _format_ass_time
from scripts.video_engine.engines.explainer_bridge import scenes_to_explainer_spec
from scripts.video_engine.scene_builder import align_checkpoints_to_timeline
from scripts.video_engine.scorm.scorm_packager import build_scorm_package


class TestEducAIVideoEngine(unittest.TestCase):

    def test_ass_time_formatting(self):
        """Verify ASS timestamp formatting."""
        self.assertEqual(_format_ass_time(0.0), "0:00:00.00")
        self.assertEqual(_format_ass_time(65.34), "0:01:05.34")
        self.assertEqual(_format_ass_time(3661.5), "1:01:01.50")

    def test_checkpoint_timeline_alignment(self):
        """Verify Invariant 1: checkpoints strictly placed at or after scene end."""
        timeline_scenes = [
            {"scene_id": "scene_01", "start": 0.0, "end": 12.4, "duration": 12.4},
            {"scene_id": "scene_02", "start": 13.0, "end": 25.8, "duration": 12.8},
        ]
        raw_cps = [
            {"scene_id": "scene_01", "question": "Pregunta 1", "options": ["A", "B"], "correct_index": 0},
            {"scene_id": "scene_02", "question": "Pregunta 2", "options": ["A", "B"], "correct_index": 1},
        ]

        aligned = align_checkpoints_to_timeline(raw_cps, timeline_scenes, tolerance_buffer=0.1)
        self.assertEqual(len(aligned), 2)
        # Checkpoint 1 must be at 12.4 + 0.1 = 12.5s
        self.assertAlmostEqual(aligned[0]["timestamp"], 12.5, places=2)
        # Checkpoint 2 must be at 25.8 + 0.1 = 25.9s
        self.assertAlmostEqual(aligned[1]["timestamp"], 25.9, places=2)

    def test_scenes_to_explainer_spec(self):
        """Verify compilation bridge from scenes.json to explainer.json spec."""
        scenes = [
            {
                "id": "scene_01",
                "title": "Introducción a la IA",
                "narration": "Bienvenidos al módulo sobre inteligencia artificial.",
                "screen_elements": {"bullets": ["Historia", "Modelos", "Desafíos"]},
            }
        ]
        spec = scenes_to_explainer_spec(scenes, title="Curso IA", formato="16:9", estilo="Pizarra")
        self.assertEqual(spec["meta"]["titulo"], "Curso IA")
        self.assertEqual(spec["meta"]["formato"], "16:9")
        self.assertEqual(spec["meta"]["estilo"], "Pizarra")
        self.assertEqual(len(spec["escenas"]), 1)
        self.assertEqual(spec["escenas"][0]["titulo"], "Introducción a la IA")
        self.assertEqual(spec["escenas"][0]["script"], "Bienvenidos al módulo sobre inteligencia artificial.")

    def test_scorm_packager_generation(self):
        """Verify building SCORM 1.2 zip packages with imsmanifest.xml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dummy_video = Path(tmpdir) / "video_test.mp4"
            dummy_video.write_bytes(b"\x00" * 1024)
            out_zip = Path(tmpdir) / "test_SCORM_Completo.zip"
            cps = [{
                "checkpoint_id": "cp_01",
                "timestamp": 10.0,
                "question": "¿Pregunta de prueba?",
                "options": ["Correcta", "Incorrecta"],
                "correct_index": 0,
                "explanation": "Explicación de prueba."
            }]

            build_scorm_package(
                title="Clase de Prueba",
                video_url="video_test.mp4",
                checkpoints=cps,
                output_zip=str(out_zip),
                include_video_file=str(dummy_video),
                also_build_zero_weight=True,
            )

            self.assertTrue(out_zip.is_file())
            # Zero-weight zip should also exist
            zero_zip = out_zip.with_name("test_SCORM.zip")
            self.assertTrue(zero_zip.is_file())

            # Verify contents of zip
            import zipfile
            with zipfile.ZipFile(out_zip, "r") as z:
                names = z.namelist()
                self.assertIn("imsmanifest.xml", names)
                self.assertIn("index.html", names)

                # Check imsmanifest content
                manifest_content = z.read("imsmanifest.xml").decode("utf-8")
                self.assertIn("Clase de Prueba", manifest_content)
                self.assertIn("index.html", manifest_content)


if __name__ == "__main__":
    unittest.main()
