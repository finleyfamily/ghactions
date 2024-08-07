"""Test ghactions.toolkit._context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from ghactions.toolkit._context import GithubContext, GitHubContextIssue, GitHubContextRepo

if TYPE_CHECKING:

    from pytest_mock import MockerFixture


MODULE = "ghactions.toolkit._context"


class TestGithubContext:
    """Test GithubContext."""

    def test___init__(self, environ: dict[str, str]) -> None:
        """Test __init__."""
        environ.pop("GITHUB_EVENT_PATH", "")
        ctx = GithubContext(event={"name": "foo"})
        assert ctx.env == environ
        assert ctx.event == {"name": "foo"}
        assert ctx._payload == {}

    def test___init___payload(self, environ: dict[str, str], test_fixture_dir: Path) -> None:
        """Test __init__ with payload."""
        payload_path = test_fixture_dir / "events" / "push.json"
        environ["GITHUB_EVENT_PATH"] = str(payload_path)
        ctx = GithubContext(environ=environ, event={"name": "foo"})
        assert ctx.env == environ
        assert ctx.event == {"name": "foo"}
        assert ctx._payload == json.loads(payload_path.read_text())

    def test___init___payload_not_found(self, environ: dict[str, str], tmp_path: Path) -> None:
        """Test __init__ with payload."""
        environ["GITHUB_EVENT_PATH"] = str(tmp_path)
        ctx = GithubContext(environ=environ, event={"name": "foo"})
        assert ctx.env == environ
        assert ctx.event == {"name": "foo"}
        assert ctx._payload == {}

    @pytest.mark.parametrize("action", ["", "test"])
    def test_action(self, action: str, environ: dict[str, str]) -> None:
        """Test action."""
        if not action:
            environ.pop("GITHUB_ACTION", "")
        else:
            environ["GITHUB_ACTION"] = action
        assert GithubContext(environ=environ, event={"name": "foo"}).action == action

    def test_action_path(self, environ: dict[str, str], tmp_path: Path) -> None:
        """Test action_path."""
        environ["GITHUB_ACTION_PATH"] = str(tmp_path)
        assert GithubContext(environ=environ, event={"name": "foo"}).action_path == tmp_path

    def test_action_path_none(self, environ: dict[str, str]) -> None:
        """Test action_path is None."""
        environ.pop("GITHUB_ACTION_PATH", None)
        assert not GithubContext(environ=environ, event={"name": "foo"}).action_path

    @pytest.mark.parametrize("action_ref", [None, "test"])
    def test_action_ref(self, action_ref: str | None, environ: dict[str, str]) -> None:
        """Test action_ref."""
        if not action_ref:
            environ.pop("GITHUB_ACTION_REF", "")
        else:
            environ["GITHUB_ACTION_REF"] = action_ref
        assert GithubContext(environ=environ, event={"name": "foo"}).action_ref == action_ref

    @pytest.mark.parametrize("action_repository", [None, "test"])
    def test_action_repository(
        self,
        action_repository: str | None,
        environ: dict[str, str],
    ) -> None:
        """Test action_repository."""
        if not action_repository:
            environ.pop("GITHUB_ACTION_REPOSITORY", "")
        else:
            environ["GITHUB_ACTION_REPOSITORY"] = action_repository
        assert (
            GithubContext(environ=environ, event={"name": "foo"}).action_repository
            == action_repository
        )

    @pytest.mark.parametrize("actor", ["", "test"])
    def test_actor(self, actor: str, environ: dict[str, str]) -> None:
        """Test actor."""
        if not actor:
            environ.pop("GITHUB_ACTOR", "")
        else:
            environ["GITHUB_ACTOR"] = actor
        assert GithubContext(environ=environ, event={"name": "foo"}).actor == actor

    @pytest.mark.parametrize("api_url", ["", "test"])
    def test_api_url(self, api_url: str, environ: dict[str, str]) -> None:
        """Test actor."""
        if not api_url:
            environ.pop("GITHUB_API_URL", "")
        else:
            environ["GITHUB_API_URL"] = api_url
        assert GithubContext(environ=environ, event={"name": "foo"}).api_url == (
            api_url or "https://api.github.com"
        )

    @pytest.mark.parametrize("base_ref", [None, "test"])
    def test_base_ref(self, base_ref: str | None, environ: dict[str, str]) -> None:
        """Test actor."""
        if not base_ref:
            environ.pop("GITHUB_BASE_REF", "")
        else:
            environ["GITHUB_BASE_REF"] = base_ref
        assert GithubContext(environ=environ, event={"name": "foo"}).base_ref == base_ref

    @pytest.mark.parametrize("event_name", ["", "test"])
    def test_event_name(self, event_name: str, environ: dict[str, str]) -> None:
        """Test actor."""
        if not event_name:
            environ.pop("GITHUB_EVENT_NAME", "")
        else:
            environ["GITHUB_EVENT_NAME"] = event_name
        assert GithubContext(environ=environ, event={"name": "foo"}).event_name == event_name

    def test_event_path(self, environ: dict[str, str], tmp_path: Path) -> None:
        """Test event_path."""
        environ["GITHUB_EVENT_PATH"] = str(tmp_path)
        assert GithubContext(environ=environ, event={"name": "foo"}).event_path == tmp_path

    def test_event_path_none(self, environ: dict[str, str]) -> None:
        """Test event_path is None."""
        environ.pop("GITHUB_EVENT_PATH", None)
        assert not GithubContext(environ=environ, event={"name": "foo"}).event_path

    def test_from_file(self, environ: dict[str, str], test_fixture_dir: Path) -> None:
        """Test from_file."""
        event_path = test_fixture_dir / "events" / "push.json"
        ctx: GithubContext[dict[str, str]] = GithubContext.from_file(event_path=event_path)
        assert ctx.env == environ
        assert ctx.event == json.loads(event_path.read_text())
        assert ctx.event_path == event_path

    def test_from_file_env(self, environ: dict[str, str], test_fixture_dir: Path) -> None:
        """Test from_file."""
        event_path = test_fixture_dir / "events" / "push.json"
        environ["GITHUB_EVENT_PATH"] = str(event_path)
        ctx: GithubContext[dict[str, str]] = GithubContext.from_file(environ=environ)
        assert ctx.env == environ
        assert ctx.event == json.loads(event_path.read_text())
        assert ctx.event_path == event_path

    def test_from_file_not_found(self, environ: dict[str, str]) -> None:
        """Test from_file raise FileNotFoundError."""
        environ.pop("GITHUB_EVENT_PATH", None)
        with pytest.raises(FileNotFoundError):
            GithubContext.from_file(environ=environ)

    @pytest.mark.parametrize("graphql_url", ["", "test"])
    def test_graphql_url(self, graphql_url: str, environ: dict[str, str]) -> None:
        """Test actor."""
        if not graphql_url:
            environ.pop("GITHUB_GRAPHQL_URL", "")
        else:
            environ["GITHUB_GRAPHQL_URL"] = graphql_url
        assert GithubContext(environ=environ, event={"name": "foo"}).graphql_url == (
            graphql_url or "https://api.github.com/graphql"
        )

    @pytest.mark.parametrize("head_ref", [None, "test"])
    def test_head_ref(self, head_ref: str | None, environ: dict[str, str]) -> None:
        """Test actor."""
        if not head_ref:
            environ.pop("GITHUB_HEAD_REF", "")
        else:
            environ["GITHUB_HEAD_REF"] = head_ref
        assert GithubContext(environ=environ, event={"name": "foo"}).head_ref == head_ref

    @pytest.mark.parametrize(
        ("event", "expected"),
        [
            ({}, None),
            ({"number": "9"}, "9"),
            ({"issue": {"number": "9"}}, "9"),
            ({"pull_request": {"number": "9"}}, "9"),
        ],
    )
    def test_issue(
        self,
        environ: dict[str, str],
        event: dict[str, Any],
        expected: str | None,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test issue."""
        event_path = tmp_path / "event.json"
        event_path.write_text(json.dumps(event))
        repo = GitHubContextRepo("user", "repo")
        mocker.patch.object(GithubContext, "repository", repo)
        assert GithubContext.from_file(environ=environ, event_path=event_path).issue == (
            GitHubContextIssue(repo.owner, repo.name, expected) if expected else None
        )

    @pytest.mark.parametrize("job", [None, "test"])
    def test_job(self, job: str | None, environ: dict[str, str]) -> None:
        """Test job."""
        if not job:
            environ.pop("GITHUB_JOB", "")
        else:
            environ["GITHUB_JOB"] = job
        assert GithubContext(environ=environ, event={"name": "foo"}).job == job

    @pytest.mark.parametrize("ref", ["", "test"])
    def test_ref(self, ref: str, environ: dict[str, str]) -> None:
        """Test ref."""
        if not ref:
            environ.pop("GITHUB_REF", "")
        else:
            environ["GITHUB_REF"] = ref
        assert GithubContext(environ=environ, event={"name": "foo"}).ref == ref

    @pytest.mark.parametrize("ref_name", ["", "test"])
    def test_ref_name(self, ref_name: str, environ: dict[str, str]) -> None:
        """Test ref_name."""
        if not ref_name:
            environ.pop("GITHUB_REF_NAME", "")
        else:
            environ["GITHUB_REF_NAME"] = ref_name
        assert GithubContext(environ=environ, event={"name": "foo"}).ref_name == ref_name

    @pytest.mark.parametrize("ref_protected", [False, True])
    def test_ref_protected(self, ref_protected: bool, environ: dict[str, str]) -> None:
        """Test ref_protected."""
        if not ref_protected:
            environ.pop("GITHUB_REF_PROTECTED", "")
        else:
            environ["GITHUB_REF_PROTECTED"] = str(ref_protected)
        assert GithubContext(environ=environ, event={"name": "foo"}).ref_protected is ref_protected

    @pytest.mark.parametrize("ref_type", ["", "branch", "tag", "test"])
    def test_ref_type(self, ref_type: str, environ: dict[str, str]) -> None:
        """Test ref_type."""
        if not ref_type:
            environ.pop("GITHUB_REF_TYPE", "")
        else:
            environ["GITHUB_REF_TYPE"] = ref_type
        assert GithubContext(environ=environ, event={"name": "foo"}).ref_type == (
            ref_type or "branch"
        )

    @pytest.mark.parametrize(
        "repository", [None, GitHubContextRepo("user", "repo"), GitHubContextRepo("org", "repo")]
    )
    def test_repository(
        self, repository: GitHubContextRepo | None, environ: dict[str, str]
    ) -> None:
        """Test repository."""
        environ.pop("GITHUB_EVENT_PATH", None)
        if not repository:
            environ.pop("GITHUB_REPOSITORY", "")
        else:
            environ["GITHUB_REPOSITORY"] = f"{repository.owner}/{repository.name}"
        assert GithubContext(environ=environ, event={"name": "foo"}).repository == repository

    def test_repository_from_event(self, environ: dict[str, str], test_fixture_dir: Path) -> None:
        """Test repository extracted from event payload."""
        environ.pop("GITHUB_REPOSITORY", None)
        environ["GITHUB_EVENT_PATH"] = str(test_fixture_dir / "events" / "push.json")
        assert GithubContext(
            environ=environ, event={"name": "foo"}
        ).repository == GitHubContextRepo("finleyfamily", "ghactions")

    def test_repository_url(self, environ: dict[str, str], mocker: MockerFixture) -> None:
        """Test repository_url."""
        repo = GitHubContextRepo("user", "repo")
        mocker.patch.object(GithubContext, "repository", repo)
        assert (
            GithubContext(environ=environ, event={"name": "foo"}).repository_url
            == f"https://github.com/{repo.owner}/{repo.name}"
        )

    def test_repository_url_none(self, environ: dict[str, str], mocker: MockerFixture) -> None:
        """Test repository_url."""
        mocker.patch.object(GithubContext, "repository", None)
        assert not GithubContext(environ=environ, event={"name": "foo"}).repository_url

    @pytest.mark.parametrize("server_url", ["", "test"])
    def test_server_url(self, server_url: str, environ: dict[str, str]) -> None:
        """Test server_url."""
        if not server_url:
            environ.pop("GITHUB_SERVER_URL", "")
        else:
            environ["GITHUB_SERVER_URL"] = server_url
        assert GithubContext(environ=environ, event={"name": "foo"}).server_url == (
            server_url or "https://github.com"
        )

    @pytest.mark.parametrize("sha", ["", "test"])
    def test_sha(self, sha: str, environ: dict[str, str]) -> None:
        """Test sha."""
        if not sha:
            environ.pop("GITHUB_SHA", "")
        else:
            environ["GITHUB_SHA"] = sha
        assert GithubContext(environ=environ, event={"name": "foo"}).sha == sha

    @pytest.mark.parametrize("token", ["", "test"])
    def test_token(self, token: str, environ: dict[str, str]) -> None:
        """Test token."""
        if not token:
            environ.pop("GITHUB_TOKEN", "")
        else:
            environ["GITHUB_TOKEN"] = token
        assert GithubContext(environ=environ, event={"name": "foo"}).token == token

    @pytest.mark.parametrize("triggering_actor", ["", "test"])
    def test_triggering_actor(self, triggering_actor: str, environ: dict[str, str]) -> None:
        """Test triggering_actor."""
        if not triggering_actor:
            environ.pop("GITHUB_TRIGGERING_ACTOR", "")
        else:
            environ["GITHUB_TRIGGERING_ACTOR"] = triggering_actor
        assert (
            GithubContext(environ=environ, event={"name": "foo"}).triggering_actor
            == triggering_actor
        )

    @pytest.mark.parametrize("workflow", ["", "test"])
    def test_workflow(self, workflow: str, environ: dict[str, str]) -> None:
        """Test workflow."""
        if not workflow:
            environ.pop("GITHUB_WORKFLOW", "")
        else:
            environ["GITHUB_WORKFLOW"] = workflow
        assert GithubContext(environ=environ, event={"name": "foo"}).workflow == workflow

    @pytest.mark.parametrize("workflow_ref", ["", "test"])
    def test_workflow_ref(self, workflow_ref: str, environ: dict[str, str]) -> None:
        """Test workflow_ref."""
        if not workflow_ref:
            environ.pop("GITHUB_WORKFLOW_REF", "")
        else:
            environ["GITHUB_WORKFLOW_REF"] = workflow_ref
        assert GithubContext(environ=environ, event={"name": "foo"}).workflow_ref == workflow_ref

    @pytest.mark.parametrize("workflow_sha", ["", "test"])
    def test_workflow_sha(self, workflow_sha: str, environ: dict[str, str]) -> None:
        """Test workflow_sha."""
        if not workflow_sha:
            environ.pop("GITHUB_WORKFLOW_SHA", "")
        else:
            environ["GITHUB_WORKFLOW_SHA"] = workflow_sha
        assert GithubContext(environ=environ, event={"name": "foo"}).workflow_sha == workflow_sha

    def test_workspace(self, environ: dict[str, str], tmp_path: Path) -> None:
        """Test workspace."""
        environ["GITHUB_WORKSPACE"] = str(tmp_path)
        assert GithubContext(environ=environ, event={"name": "foo"}).workspace == tmp_path

    def test_workspace_cwd(self, environ: dict[str, str]) -> None:
        """Test workspace is cwd."""
        environ.pop("GITHUB_WORKSPACE", None)
        assert GithubContext(environ=environ, event={"name": "foo"}).workspace == Path.cwd()
