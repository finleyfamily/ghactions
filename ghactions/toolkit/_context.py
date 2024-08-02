"""Github context."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, MutableMapping
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

EventTypeVar = TypeVar("EventTypeVar", BaseModel, Mapping[str, Any], MutableMapping[str, Any])


class GitHubContextIssue(NamedTuple):
    """GitHub Issue split into it's components for :class:`ghactions.toolkit.GithubContext`."""

    owner: str
    """Owner of the repository."""

    repo: str
    """Name of the repository."""

    number: str
    """Issue number."""


class GitHubContextRepo(NamedTuple):
    """GitHub Repository split into it's components for :class:`ghactions.toolkit.GithubContext`."""

    owner: str
    """Owner of the repository."""

    name: str
    """Name of the repository."""


class GithubContext(Generic[EventTypeVar]):
    """Webhook payload object that triggered the workflow.

    https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/contexts#github-context

    """

    _payload: dict[str, Any]
    """Raw payload."""

    env: dict[str, str]
    """Environment variables."""

    event: EventTypeVar
    """Event that triggered the workflow.

    Optionally parsed into a :class:`pydantic.BaseModel` if able.

    """

    def __init__(
        self,
        *,
        environ: dict[str, str] | None = None,
        event: EventTypeVar,
        event_path: Path | None = None,
    ) -> None:
        """Instantiate object.

        Args:
            environ: Environment variables.
            event: The event that triggered the workflow.
            event_path: Manually specificy the path to the event file that was loaded.

        """
        self._event_path = event_path
        self.env = environ or os.environ.copy()
        self.event = event

        if self.event_path and self.event_path.is_file():
            self._payload = json.loads(self.event_path.read_text())
        else:
            self._payload = {}

    @property
    def action(self) -> str:
        """The name of the action currently running, or the id of a step (from environment variables).

        GitHub removes special characters, and uses the name ``__run`` when the
        current step runs a script without an id.
        If you use the same action more than once in the same job,
        the name will include a suffix with the sequence number with underscore before it.

        """
        return self.env.get("GITHUB_ACTION", "")

    @property
    def action_path(self) -> Path | None:
        """The path where an action is located (from environment variables).

        This property is only supported in composite actions.
        You can use this path to access files located in the same repository as the action.

        """
        value = self.env.get("GITHUB_ACTION_PATH")
        return Path(value) if value else None

    @property
    def action_ref(self) -> str | None:
        """For a step executing an action, this is the ref of the action being executed."""
        return self.env.get("GITHUB_ACTION_REF")

    @property
    def action_repository(self) -> str | None:
        """For a step executing an action, this is the owner and repository name of the action."""
        return self.env.get("GITHUB_ACTION_REPOSITORY")

    @property
    def actor(self) -> str:
        """The username of the user that triggered the initial workflow run (from environment variables)."""
        return self.env.get("GITHUB_ACTOR", "")

    @property
    def api_url(self) -> str:
        """The URL of the GitHub REST API (from environment variables)."""
        return self.env.get("GITHUB_API_URL", "https://api.github.com")

    @property
    def base_ref(self) -> str | None:
        """The ``base_ref`` or target branch of the pull request in a workflow run (from environment variables).

        This property is only available when the event that triggers a workflow
        run is either ``pull_request`` or ``pull_request_target``.

        """
        return self.env.get("GITHUB_BASE_REF")

    @property
    def event_name(self) -> str:
        """The name of the event that triggered the workflow run (from environment variables)."""
        return self.env.get("GITHUB_EVENT_NAME", "")

    @property
    def event_path(self) -> Path | None:
        """The path to the file on the runner that contains the full event webhook payload ."""
        value = self._event_path or self.env.get("GITHUB_EVENT_PATH")
        return Path(value) if value else None

    @property
    def graphql_url(self) -> str:
        """The URL of the GitHub GraphQL API (from environment variables)."""
        return self.env.get("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")

    @property
    def head_ref(self) -> str | None:
        """The ``head_ref`` or source branch of the pull request in a workflow run (from environment variables).

        This property is only available when the event that triggers a workflow
        run is either ``pull_request`` or ``pull_request_target``.

        """
        return self.env.get("GITHUB_HEAD_REF")

    @cached_property
    def issue(self) -> GitHubContextIssue | None:
        """GitHub Issue."""
        payload = self._payload.get("issue") or self._payload.get("pull_request") or self._payload
        number = payload.get("number")
        if not number or not self.repository:
            return None
        return GitHubContextIssue(self.repository.owner, self.repository.name, number)

    @property
    def job(self) -> str | None:
        """The ``job_id`` of the current job (from environment variables).

        .. note::
            This context property is set by the Actions runner, and is only available
            within the execution ``steps`` of a job.
            Otherwise, the value of this property will be :data:`None`.

        """
        return self.env.get("GITHUB_JOB")

    @property
    def ref(self) -> str:
        """The fully-formed ref of the branch or tag that triggered the workflow run (from environment variables).

        For workflows triggered by ``push``, this is the branch or tag ref that was pushed.
        For workflows triggered by ``pull_request``, this is the pull request merge branch.
        For workflows triggered by ``release``, this is the release tag created.
        For other triggers, this is the branch or tag ref that triggered the workflow run.

        This is only set if a branch or tag is available for the event type.
        The ref given is fully-formed, meaning that for branches the format is
        ``refs/heads/<branch_name>``, for pull requests it is ``refs/pull/<pr_number>/merge``,
        and for tags it is ``refs/tags/<tag_name>``.

        """
        return self.env.get("GITHUB_REF", "")

    @property
    def ref_name(self) -> str:
        """The short ref name of the branch or tag that triggered the workflow run (from environment variables).

        This value matches the branch or tag name shown on GitHub.
        For pull requests, the format is ``<pr_number>/merge``.

        """
        return self.env.get("GITHUB_REF_NAME", "")

    @property
    def ref_protected(self) -> bool:
        """If branch protections or rulesets are configured for the ref that triggered the workflow."""
        return self.env.get("GITHUB_REF_PROTECTED", "").lower() in ("1", "true")

    @property
    def ref_type(self) -> str:
        """The type of ref that triggered the workflow run (from environment variables).

        Valid values are ``branch`` or ``tag``.

        """
        return self.env.get("GITHUB_REF_TYPE", "branch")

    @cached_property
    def repository(self) -> GitHubContextRepo | None:
        """GitHub Repository."""
        repo = self.env.get("GITHUB_REPOSITORY")
        if self.env.get("GITHUB_REPOSITORY"):
            return GitHubContextRepo(*self.env["GITHUB_REPOSITORY"].split("/"))
        repo = self._payload.get("repository")
        if not repo:
            return None
        return GitHubContextRepo(repo["owner"]["login"], repo["name"])

    @property
    def repository_url(self) -> str | None:
        """The Git URL to the repository (from environment variables)."""
        return (
            f"{self.server_url}/{self.repository.owner}/{self.repository.name}"
            if self.repository
            else None
        )

    @property
    def server_url(self) -> str:
        """The URL of the GitHub server (from environment variables)."""
        return self.env.get("GITHUB_SERVER_URL", "https://github.com")

    @property
    def sha(self) -> str:
        """The commit SHA that triggered the workflow (from environment variables).

        The value of this commit SHA depends on the event that triggered the workflow.

        """
        return self.env.get("GITHUB_SHA", "")

    @property
    def token(self) -> str:
        """A token to authenticate on behalf of the GitHub App installed on your repository.

        This is functionally equivalent to the ``GITHUB_TOKEN`` secret/environment variable.

        """
        return self.env.get("GITHUB_TOKEN", "")

    @property
    def triggering_actor(self) -> str:
        """The username of the user that initiated the workflow run (from environment variables)."""
        return self.env.get("GITHUB_TRIGGERING_ACTOR", "")

    @property
    def workflow(self) -> str:
        """The name of the workflow (from environment variables).

        If the workflow file doesn't specify a ``name``, the value of this property
        is the full path of the workflow file in the repository.

        """
        return self.env.get("GITHUB_WORKFLOW", "")

    @property
    def workflow_ref(self) -> str:
        """The ref path to the workflow (from environment variables).

        For example, ``octocat/hello-world/.github/workflows/my-workflow.yml@refs/heads/my_branch``.

        """
        return self.env.get("GITHUB_WORKFLOW_REF", "")

    @property
    def workflow_sha(self) -> str:
        """The commit SHA for the workflow file (from environment variables)."""
        return self.env.get("GITHUB_WORKFLOW_SHA", "")

    @property
    def workspace(self) -> Path:
        """The default working directory on the runner for steps (from environment variables).

        Also the default location of your repository when using the ``checkout`` action.

        """
        value = self.env.get("GITHUB_WORKSPACE")
        return Path(value) if value else Path.cwd()

    @classmethod
    def from_file(
        cls: type[Self],
        *,
        environ: dict[str, str] | None = None,
        event_path: Path | str | None = None,
    ) -> Self:
        """Load event from a file.

        Args:
            environ: Environment variables.
            event_path: Path to the JSON file containing the event.

        """
        if not event_path:
            event_path = os.getenv("GITHUB_EVENT_PATH", "")
        event_path = Path(event_path) if not isinstance(event_path, Path) else event_path
        if not event_path.is_file():
            raise FileNotFoundError(event_path)
        return cls(environ=environ, event=json.loads(event_path.read_text()), event_path=event_path)
