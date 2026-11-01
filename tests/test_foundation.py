"""Foundation domain behavior on temporary databases; no Qt, network or commercial media."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from orvex.core.store import Store
from orvex.foundation.models import Content, ContentUnavailable, ProposalConflict, source_identity
from orvex.foundation.profiles import AuthenticationUnavailable, ProfileService
from orvex.foundation.services import FoundationServices


class TestAuthorizer:
    """Test-only proof checker. Not an implementation of a PIN service."""

    def require(self, profile_id, scope, proof):
        if proof != "test-proof" or scope != "manage_profiles":
            raise PermissionError("Denied")


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "catalog.sqlite3")
        self.services = FoundationServices(self.store)
        self.catalog = self.services.catalog

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def add(self, title="Una película", kind="movie", age=7, **kwargs):
        return self.catalog.register(
            "adult",
            kind=kind,
            title=title,
            age=age,
            source_type="local",
            source_ref=str(self.root / (title + ".media")),
            **kwargs,
        ).content

    def test_all_content_kinds_and_episode_parent_persist(self):
        series = self.add("Serie", kind="series")
        episode = self.add("Episodio", kind="episode", parent_id=series.id)
        for kind in ("game", "movie", "application"):
            self.add(kind, kind=kind)
        self.assertEqual(
            {c.kind for c in self.catalog.query("adult")},
            {"game", "movie", "series", "episode", "application"},
        )
        reopened = Store(self.store.path)
        try:
            query = FoundationServices(reopened).catalog
            self.assertEqual(query.get(episode.id, "adult").parent_id, series.id)
            self.assertEqual(len(query.query("adult")), 5)
        finally:
            reopened.close()
        with self.assertRaises(ValueError):
            self.add("Sin serie", kind="episode")
        with self.assertRaises(ValueError):
            self.add("Padre incorrecto", kind="episode", parent_id=episode.id)
        with self.assertRaises(ValueError):
            self.add("No episodio", parent_id=series.id)

    def test_register_never_executes_and_duplicates_preserve_approved_data(self):
        marker = self.root / "never-ran"
        first = self.catalog.register(
            "adult",
            kind="application",
            title="Original",
            source_type="local",
            source_ref=str(marker),
            metadata={"description": "Aprobada"},
        )
        again = self.catalog.register(
            "adult",
            kind="application",
            title="No reemplazar",
            source_type="local",
            source_ref=str(self.root / "sub" / ".." / "never-ran"),
        )
        self.assertTrue(first.created)
        self.assertFalse(again.created)
        self.assertEqual(again.content.id, first.content.id)
        self.assertEqual(again.content.title, "Original")
        self.assertFalse(marker.exists())
        self.assertEqual(len(self.catalog.query("adult")), 1)
        with self.assertRaises(ValueError):
            self.catalog.register(
                "adult", kind="game", title="Otro tipo", source_type="local", source_ref=str(marker)
            )

    def test_windows_source_identity_and_external_ids(self):
        first = self.catalog.register(
            "adult",
            kind="game",
            title="Game",
            source_type="local",
            source_ref=r"C:\Games\Folder\..\Game.EXE",
        )
        duplicate = self.catalog.register(
            "adult",
            kind="game",
            title="Another",
            source_type="local",
            source_ref="c:/games/game.exe",
        )
        self.assertEqual(first.content.id, duplicate.content.id)
        ext = self.catalog.register(
            "adult",
            kind="movie",
            title="Reference only",
            source_type="provider-id",
            source_ref="ABC-42",
        )
        self.assertEqual(ext.content.import_state, "registered")
        with self.assertRaises(ValueError):
            self.catalog.register(
                "adult",
                kind="movie",
                title="Invalid",
                source_type="local",
                source_ref="relative/file.mp4",
            )

    def test_windows_short_alias_and_resolved_path_share_source_identity(self):
        # Simulated Windows filesystem resolution; the native Windows integration test
        # also exercises actual TemporaryDirectory aliases when the runner uses 8.3 paths.
        short = r"C:\Users\RUNNER~1\Games\owned.iso"
        canonical = r"C:\Users\RunnerAdmin\Games\owned.iso"
        with patch("orvex.foundation.models.sys.platform", "win32"):
            with patch("orvex.foundation.models.Path") as native_path:
                native_path.return_value.resolve.return_value = canonical
                self.assertEqual(
                    source_identity("local", short), source_identity("local", canonical)
                )

    def test_search_alternate_title_filters_and_profile_favorites(self):
        safe = self.add("Océano", alternate_title="Ocean", format="MKV")
        restricted = self.add("Oscuridad", age=18, format="MP4")
        self.catalog.favorite(safe.id, "adult", True)
        self.catalog.favorite(safe.id, "child", True)
        self.catalog.favorite(restricted.id, "adult", True)
        self.assertEqual(
            [c.id for c in self.catalog.query("child", query="OCEANO", kind="movie", format="MKV")],
            [safe.id],
        )
        self.assertEqual([c.id for c in self.catalog.query("child", query="ocean")], [safe.id])
        self.assertEqual(self.catalog.options("child"), ["MKV"])
        self.catalog.favorite(safe.id, "adult", False)
        self.assertEqual(
            [c.id for c in self.catalog.query("child", favorites_only=True)], [safe.id]
        )
        self.assertEqual(
            [c.id for c in self.catalog.query("adult", favorites_only=True)], [restricted.id]
        )
        self.assertEqual(self.catalog.query("unknown"), [])
        with self.assertRaises(ContentUnavailable):
            self.catalog.get(restricted.id, "child")
        with self.assertRaises(PermissionError):
            self.catalog.register(
                "child", kind="movie", title="Blocked", source_type="id", source_ref="x"
            )

    def test_age_policy_matches_shared_python_javascript_cases(self):
        cases = json.loads((Path(__file__).parent / "fixtures/age_policy.json").read_text())
        for case in cases:
            entry = case["entry"]
            if not isinstance(entry, dict) or case["profile"] not in ("adult", "child"):
                continue
            item = Content("test", "movie", "Test", "", "", "id", "test", age=entry.get("age"))
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    ProfileService.allows(self.services.profiles.get(case["profile"]), item),
                    case["allowed"],
                )
        for age in (float("nan"), float("inf"), 10**1000, True, "7", -1, 7.5):
            item = Content("test", "movie", "Test", "", "", "id", "test", age=age)
            self.assertFalse(ProfileService.allows(self.services.profiles.get("child"), item))

    def test_restricted_parent_hides_episode_art_search_recent_and_favorites(self):
        series = self.add("Serie adulta", kind="series", age=18)
        episode = self.add(
            "Episodio aparentemente infantil",
            kind="episode",
            parent_id=series.id,
            age=3,
            cover="private-cover.png",
            backdrop="private-background.png",
        )
        self.catalog.favorite(episode.id, "adult", True)
        self.catalog.record_activity(episode.id, "adult")
        self.store.set_favorite(
            "child", episode.id, True
        )  # stale favorite from before classification
        self.assertEqual(self.catalog.query("child"), [])
        self.assertEqual(self.catalog.options("child"), [])
        self.assertEqual(self.catalog.recent("child"), [])
        self.assertEqual(
            self.catalog.query("child", query="aparentemente", favorites_only=True), []
        )
        with self.assertRaises(ContentUnavailable):
            self.catalog.get(episode.id, "child")
        with self.assertRaises(ContentUnavailable):
            self.catalog.record_activity(episode.id, "child")

    def test_activity_profiles_and_disabled_profile_fail_closed(self):
        movie = self.add(age=3)
        self.catalog.record_activity(
            movie.id, "adult", event="finished", duration_ms=1000, evidence="observed"
        )
        self.assertEqual(self.catalog.recent("child"), [])
        self.catalog.record_activity(movie.id, "child")
        self.assertEqual([c.id for c in self.catalog.recent("child")], [movie.id])
        self.assertIsNone(self.catalog.activity("child")[0]["duration_ms"])
        self.assertEqual(self.catalog.activity("adult")[0]["duration_ms"], 1000)
        with self.store.transaction():
            self.store.db.execute("UPDATE profiles SET enabled=0 WHERE id='child'")
        self.assertEqual(self.catalog.query("child"), [])
        self.assertEqual(self.catalog.activity("child"), [])
        with self.assertRaises(ContentUnavailable):
            self.catalog.get(movie.id, "child")
        for invalid in (-1, True, 1.2, 2**64):
            with self.assertRaises(ValueError):
                self.catalog.record_activity(
                    movie.id, "adult", event="finished", duration_ms=invalid
                )

    def test_proposals_require_approval_and_reject_stale_or_double_approval(self):
        original = self.add(
            metadata={"description": "Old", "genre": "Keep"}, cover="approved-cover.png"
        )
        proposal = self.catalog.propose_metadata(
            original.id,
            "adult",
            {"metadata": {"description": "New"}, "alternate_title": "Other"},
            "local review fixture",
        )
        self.assertEqual(self.catalog.get(original.id, "adult").metadata["description"], "Old")
        with self.assertRaises(PermissionError):
            self.catalog.decide_proposal(proposal, "child", True)
        updated = self.catalog.decide_proposal(proposal, "adult", True)
        self.assertEqual(updated.metadata["description"], "New")
        self.assertEqual(updated.metadata["genre"], "Keep")
        self.assertEqual(updated.cover, "approved-cover.png")
        with self.assertRaises(ProposalConflict):
            self.catalog.decide_proposal(proposal, "adult", True)
        stale = self.catalog.propose_metadata(original.id, "adult", {"title": "Stale"}, "local")
        newer = self.catalog.propose_metadata(
            original.id, "adult", {"title": "Approved newer"}, "local"
        )
        self.catalog.decide_proposal(newer, "adult", True)
        with self.assertRaises(ProposalConflict):
            self.catalog.decide_proposal(stale, "adult", True)
        self.assertEqual(self.catalog.proposal(stale, "adult")["state"], "pending")
        self.catalog.decide_proposal(stale, "adult", False)
        self.assertEqual(self.catalog.get(original.id, "adult").title, "Approved newer")

    def test_metadata_failure_is_atomic_and_bad_input_is_conservative(self):
        movie = self.add()
        proposal = self.catalog.propose_metadata(
            movie.id, "adult", {"title": "Never committed"}, "local"
        )
        original_update = self.services.repository.update

        def fail(content):
            original_update(content)
            raise RuntimeError("injected storage fault")

        with patch.object(self.services.repository, "update", side_effect=fail):
            with self.assertRaises(RuntimeError):
                self.catalog.decide_proposal(proposal, "adult", True)
        self.assertEqual(self.catalog.get(movie.id, "adult").title, movie.title)
        self.assertEqual(self.catalog.proposal(proposal, "adult")["state"], "pending")
        for changes in (
            {"age": True},
            {"age": "7"},
            {"executable": "malicious"},
            {"metadata": []},
            {"title": ""},
        ):
            with self.assertRaises(ValueError):
                self.catalog.propose_metadata(movie.id, "adult", changes, "local")
        for invalid in ("bad json", [], {"value": float("nan")}):
            with self.assertRaises(ValueError):
                self.add("Bad metadata", metadata=invalid)

    def test_profile_ids_and_pin_contract_no_false_authentication(self):
        with self.assertRaises(AuthenticationUnavailable):
            self.services.profiles.create("adult", "Otro", "child", 5, proof="1234")
        authorized = FoundationServices(self.store, authorizer=TestAuthorizer())
        with self.assertRaises(PermissionError):
            authorized.profiles.create("child", "Adulto", "adult", proof="test-proof")
        with self.assertRaises(PermissionError):
            authorized.profiles.create("adult", "Otro", "child", 5, proof="wrong")
        profile = authorized.profiles.create(
            "adult", "Otro infantil", "child", 5, proof="test-proof"
        )
        self.assertEqual(
            [p.id for p in self.services.profiles.list_profiles(profile.id)], [profile.id]
        )
        self.assertIn(profile.id, [p.id for p in self.services.profiles.list_profiles("adult")])
        movie = self.add(age=3)
        self.catalog.favorite(movie.id, profile.id, True)
        self.assertEqual(self.catalog.query("adult", favorites_only=True), [])
        reopened = Store(self.store.path)
        try:
            services = FoundationServices(reopened)
            self.assertEqual(services.profiles.get(profile.id).max_age, 5)
            self.assertEqual(
                [c.id for c in services.catalog.query(profile.id, favorites_only=True)], [movie.id]
            )
        finally:
            reopened.close()

    def test_legacy_projection_reuses_favorites_and_detects_outside_edits(self):
        with self.store.transaction():
            self.store.db.execute(
                "INSERT INTO real_games(id,name,platform,executable,created_at,metadata) VALUES('old','Legacy','Wii',?,'2026-01-01',?)",
                (str(self.root / "old.exe"), '{"description":"Preserved"}'),
            )
            self.store.db.execute(
                "INSERT INTO play_sessions(game_id,started_at,status,duration_ms) VALUES('old','2026-01-01','finished',457800)"
            )
        self.assertTrue(self.catalog.get("old", "adult").legacy_game)
        self.assertEqual(
            self.store.db.execute("SELECT COUNT(*) FROM content_items").fetchone()[0], 0
        )
        self.assertEqual(self.catalog.activity("adult"), [])  # old profile unknown, not guessed
        duplicate = self.catalog.register(
            "adult",
            kind="game",
            title="Do not duplicate",
            source_type="local",
            source_ref=str(self.root / "old.exe"),
        )
        self.assertFalse(duplicate.created)
        self.catalog.favorite("old", "adult", True)
        self.assertEqual(self.store.favorites("adult"), ["old"])
        proposal = self.catalog.propose_metadata(
            "old", "adult", {"title": "Reviewed", "age": 7}, "local"
        )
        other = Store(self.store.path)
        try:
            with other.transaction():
                other.db.execute("UPDATE real_games SET name='Changed by 0.4' WHERE id='old'")
        finally:
            other.close()
        with self.assertRaises(ProposalConflict):
            self.catalog.decide_proposal(proposal, "adult", True)
        proposal = self.catalog.propose_metadata(
            "old", "adult", {"title": "Reviewed", "age": 7}, "local"
        )
        self.catalog.decide_proposal(proposal, "adult", True)
        self.assertEqual(
            self.store.db.execute("SELECT name,metadata,executable FROM real_games").fetchone(),
            ("Reviewed", '{"description": "Preserved"}', str(self.root / "old.exe")),
        )
        self.assertEqual(self.catalog.get("old", "child").age, 7)
        self.assertEqual(
            self.store.db.execute("SELECT duration_ms,profile_id FROM play_sessions").fetchone(),
            (457800, None),
        )

    def test_service_cli_work_without_qt_and_no_external_provider_is_claimed(self):
        script = """
import sys
class NoQt:
 def find_spec(self,fullname,path=None,target=None):
  if fullname.startswith('PySide6'):raise AssertionError('Qt imported by domain')
sys.meta_path.insert(0,NoQt())
from orvex.core.store import Store
from orvex.foundation.services import FoundationServices
s=Store(':memory:'); c=FoundationServices(s).catalog
c.register('adult',kind='movie',title='Offline',source_type='local-id',source_ref='1')
assert len(c.query('adult'))==1
s.close()
"""
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1] / "src"))
        subprocess.run([sys.executable, "-c", script], env=env, check=True, capture_output=True)
        command = [sys.executable, "-m", "orvex.foundation", "--database", str(self.store.path)]
        result = subprocess.run(
            command
            + [
                "register",
                "--kind",
                "movie",
                "--title",
                "CLI movie",
                "--source-type",
                "local-id",
                "--source-ref",
                "cli",
            ],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue(json.loads(result.stdout)["created"])
        result = subprocess.run(
            command + ["list", "--search", "CLI"],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout)[0]["title"], "CLI movie")

    def test_cross_legacy_duplicates_are_reported_without_deletion_or_child_leak(self):
        reference = self.add("Registered game", kind="game", age=None)
        with self.store.transaction():
            self.store.db.execute(
                "INSERT INTO real_games(id,name,platform,executable,created_at) VALUES('imported-later','Imported later','PC',?,'2026-01-01')",
                (reference.source_ref,),
            )
        groups = self.catalog.find_duplicates("adult")
        self.assertEqual(len(groups), 1)
        self.assertEqual({c.id for c in groups[0]}, {reference.id, "imported-later"})
        self.assertEqual(self.catalog.find_duplicates("child"), [])
        self.assertEqual(
            self.store.db.execute("SELECT COUNT(*) FROM content_items").fetchone()[0], 1
        )
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM real_games").fetchone()[0], 1)
