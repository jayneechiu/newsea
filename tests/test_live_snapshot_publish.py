"""Exercise the workflow's publish script against a local protected Git remote."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "Requires Bash and Git")
class PublishSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.env = {
            **os.environ,
            "GH_TOKEN": "test-token",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": f"url.{self.remote.as_posix()}.insteadOf",
            "GIT_CONFIG_VALUE_0": "https://x-access-token:test-token@github.com/test/repo.git",
        }
        self.git("init", "--bare", "-q", str(self.remote))
        self.git("--git-dir", str(self.remote), "config", "receive.denyNonFastForwards", "true")
        workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "live-snapshot.yml")
        step = workflow.read_text(encoding="utf-8").split("      - name: Publish to live-data branch\n", 1)[1]
        script = step.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0]
        self.script = textwrap.dedent(script).replace("${{ github.repository }}", "test/repo")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], env=self.env, check=True, capture_output=True, text=True
        ).stdout.strip()

    def publish(self, content):
        runner_temp = self.root / f"runner-{len(list(self.root.glob('runner-*')))}"
        workspace = runner_temp / "workspace"
        snapshot = workspace / "live-data" / "live-cards.json"
        snapshot.parent.mkdir(parents=True)
        snapshot.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [shutil.which("bash"), "-e", "-c", self.script],
            cwd=snapshot.parent,
            env={
                **self.env,
                "RUNNER_TEMP": runner_temp.as_posix(),
                "GITHUB_WORKSPACE": workspace.as_posix(),
            },
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.git("--git-dir", str(self.remote), "rev-parse", "refs/heads/live-data")

    def test_creates_missing_live_data_branch(self):
        self.publish('{"cards": []}')
        self.assertEqual(
            self.git("--git-dir", str(self.remote), "ls-tree", "--name-only", "live-data"),
            "live-cards.json",
        )

    def test_updates_snapshot_without_rewriting_history(self):
        previous = self.publish('{"cards": []}')
        self.publish('{"cards": [{"id": "new"}]}')
        self.assertEqual(
            self.git("--git-dir", str(self.remote), "rev-parse", "live-data^"), previous
        )
        self.assertEqual(
            self.git("--git-dir", str(self.remote), "show", "live-data:live-cards.json"),
            '{"cards": [{"id": "new"}]}',
        )

    def test_unchanged_snapshot_does_not_create_commit(self):
        previous = self.publish('{"cards": []}')
        self.assertEqual(self.publish('{"cards": []}'), previous)


if __name__ == "__main__":
    unittest.main()
