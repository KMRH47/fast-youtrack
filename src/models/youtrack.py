import logging
import time
from enum import StrEnum
from datetime import datetime, UTC
from typing import List, Optional, Union

from pydantic import BaseModel, Field as PydanticField, field_validator

logger = logging.getLogger(__name__)


def convert_to_iso_if_timestamp(value):
    """Convert integer timestamps to ISO format strings while preserving other values."""
    if isinstance(value, int):
        try:
            return datetime.fromtimestamp(value / 1000.0, UTC).isoformat()
        except Exception as e:
            logger.warning(f"Failed timestamp conversion: {value} - {e}")
            return str(value)
    return value


def datetime_to_unix_timestamp(datetime: datetime) -> int:
    """Convert datetime to Unix timestamp in milliseconds."""
    return int(datetime.timestamp() * 1000)


class WorkItem(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type_: Optional[str] = PydanticField(default=None, alias="$type")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {datetime: datetime_to_unix_timestamp},
    }


class UserType(WorkItem):
    pass


class User(WorkItem):
    guest: Optional[bool] = None
    banned: Optional[bool] = None
    avatarUrl: Optional[str] = None
    login: Optional[str] = None
    email: Optional[str] = None
    userType: Optional[UserType] = None
    isEmailVerified: Optional[bool] = None
    ringId: Optional[str] = None
    online: Optional[bool] = None
    canReadProfile: Optional[bool] = None
    name: Optional[str] = None
    isLocked: Optional[bool] = None
    fullName: Optional[str] = None


class FieldType(WorkItem):
    valueType: Optional[str] = None
    isMultiValue: Optional[bool] = None
    presentation: Optional[str] = None
    isBundleType: Optional[bool] = None


class Field(WorkItem):
    name: Optional[str] = None
    fieldType: Optional[FieldType] = None


class ProjectCustomField(WorkItem):
    emptyFieldText: Optional[str] = None
    field: Optional[Field] = None


class EnumBundleElement(WorkItem):
    name: Optional[str] = None
    value: Optional[Union[str, int]] = None


class CustomField(WorkItem):
    """Custom field that can contain various value types including timestamps."""

    projectCustomField: Optional[ProjectCustomField] = None
    value: Optional[
        Union[EnumBundleElement, List[EnumBundleElement], int, str, None]
    ] = None

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value_format(cls, v):
        return convert_to_iso_if_timestamp(v)


class IssueWatchers(WorkItem):
    hasStar: Optional[bool] = None


class ProjectVcsIntegrationSettings(WorkItem):
    hasVcsIntegrations: Optional[bool] = None


class ProjectTimeTrackingSettings(WorkItem):
    enabled: Optional[bool] = None


class ProjectGraziePlugin(WorkItem):
    disabled: Optional[bool] = None


class ProjectHelpDeskSettings(WorkItem):
    enabled: Optional[bool] = None
    defaultForm: Optional[str] = None


class ProjectPlugins(WorkItem):
    vcsIntegrationSettings: Optional[ProjectVcsIntegrationSettings] = None
    timeTrackingSettings: Optional[ProjectTimeTrackingSettings] = None
    grazie: Optional[ProjectGraziePlugin] = None
    helpDeskSettings: Optional[ProjectHelpDeskSettings] = None


class UserGroup(WorkItem):
    allUsersGroup: Optional[bool] = None
    ringId: Optional[str] = None
    icon: Optional[str] = None
    name: Optional[str] = None


class Project(WorkItem):
    plugins: Optional[ProjectPlugins] = None
    shortName: Optional[str] = None
    template: Optional[bool] = None
    restricted: Optional[bool] = None
    iconUrl: Optional[str] = None
    team: Optional[UserGroup] = None
    organization: Optional[str] = None
    fieldsSorted: Optional[bool] = None
    archived: Optional[bool] = None
    isDemo: Optional[bool] = None
    ringId: Optional[str] = None
    hasArticles: Optional[bool] = None
    pinned: Optional[bool] = None
    name: Optional[str] = None


class FieldStyle(WorkItem):
    background: Optional[str]
    foreground: Optional[str]


class EnumBundle(WorkItem):
    pass


class EnumProjectCustomField(WorkItem):
    bundle: Optional[EnumBundle] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class SingleEnumIssueCustomField(WorkItem):
    """Enum field that may contain timestamp values in certain cases."""

    projectCustomField: Optional[EnumProjectCustomField] = None
    value: Optional[Union[EnumBundleElement, int, str]] = None

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value_format(cls, v):
        return convert_to_iso_if_timestamp(v)


class StateBundle(WorkItem):
    pass


class StateBundleElement(WorkItem):
    isResolved: Optional[bool] = None
    localizedName: Optional[str] = None
    description: Optional[str] = None
    color: Optional[FieldStyle] = None
    name: Optional[str] = None


class StateProjectCustomField(WorkItem):
    bundle: Optional[StateBundle] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class StateIssueCustomField(WorkItem):
    projectCustomField: Optional[StateProjectCustomField] = None
    value: Optional[StateBundleElement] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class UserBundle(WorkItem):
    pass


class UserProjectCustomField(WorkItem):
    bundle: Optional[UserBundle] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class SingleUserIssueCustomField(WorkItem):
    value: Optional[str] = None
    projectCustomField: Optional[UserProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class VersionBundle(WorkItem):
    pass


class VersionProjectCustomField(WorkItem):
    bundle: Optional[VersionBundle] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class MultiVersionIssueCustomField(WorkItem):
    value: Optional[List] = None
    projectCustomField: Optional[VersionProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class PeriodProjectCustomField(WorkItem):
    isSpentTime: Optional[bool] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class PeriodIssueCustomField(WorkItem):
    value: Optional[str] = None
    projectCustomField: Optional[PeriodProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class OwnedBundle(WorkItem):
    pass


class OwnedProjectCustomField(WorkItem):
    bundle: Optional[OwnedBundle] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class MultiOwnedIssueCustomField(WorkItem):
    value: Optional[List] = None
    projectCustomField: Optional[OwnedProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class SimpleProjectCustomField(WorkItem):
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class SimpleIssueCustomField(WorkItem):
    value: Optional[str] = None
    projectCustomField: Optional[SimpleProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class DateIssueCustomField(WorkItem):
    """Date field that accepts both ISO strings and epoch timestamps."""

    value: Optional[Union[str, int]] = None
    projectCustomField: Optional[SimpleProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value_format(cls, v):
        return convert_to_iso_if_timestamp(v)


class BuildBundle(WorkItem):
    pass


class BuildProjectCustomField(WorkItem):
    bundle: Optional[BuildBundle] = None
    ordinal: Optional[int] = None
    emptyFieldText: Optional[str] = None
    canBeEmpty: Optional[bool] = None
    isPublic: Optional[bool] = None
    hasRunningJob: Optional[bool] = None
    field: Optional[Field] = None


class MultiBuildIssueCustomField(WorkItem):
    value: Optional[List] = None
    projectCustomField: Optional[BuildProjectCustomField] = None
    isUpdatable: Optional[bool] = None
    searchResults: Optional[List] = None


class IssueVoters(WorkItem):
    hasVote: Optional[bool] = None


class UnlimitedVisibility(WorkItem):
    permittedGroups: Optional[List] = None
    permittedUsers: Optional[List[User]] = None


class Channel(WorkItem):
    name: Optional[str] = None
    id: Optional[str] = None


class Issue(WorkItem):
    usesMarkdown: Optional[bool] = None
    created: Optional[int] = None
    description: Optional[str] = None
    watchers: Optional[IssueWatchers] = None
    visibility: Optional[UnlimitedVisibility] = None
    messages: Optional[List] = None
    project: Optional[Project] = None
    idReadable: Optional[str] = None
    summary: Optional[str] = None
    creator: Optional[User] = None
    updated: Optional[int] = None
    widgets: Optional[List] = None
    resolved: Optional[int] = None
    mentionedIssues: Optional[List] = None
    mentionedUsers: Optional[List] = None
    mentionedArticles: Optional[List] = None
    tags: Optional[List] = None
    attachments: Optional[List] = None
    votes: Optional[int] = None
    reporter: Optional[User] = None
    unauthenticatedReporter: Optional[bool] = None
    canUndoComment: Optional[bool] = None
    markdownEmbeddings: Optional[List] = None
    voters: Optional[IssueVoters] = None
    hasEmail: Optional[bool] = None
    pinnedComments: Optional[List] = None
    wikifiedDescription: Optional[str] = None
    updater: Optional[User] = None
    canUpdateVisibility: Optional[bool] = None
    canAddPublicComment: Optional[bool] = None
    externalIssue: Optional[str] = None
    usersTyping: Optional[List] = None
    summaryTextSearchResult: Optional[str] = None
    descriptionTextSearchResult: Optional[str] = None
    fields: Optional[
        List[
            Union[
                SingleEnumIssueCustomField,
                StateIssueCustomField,
                SingleUserIssueCustomField,
                MultiVersionIssueCustomField,
                PeriodIssueCustomField,
                MultiOwnedIssueCustomField,
                SimpleIssueCustomField,
                DateIssueCustomField,
                MultiBuildIssueCustomField,
            ]
        ]
    ] = None
    channel: Optional[Union[str, Channel]] = None


class FieldStyle(WorkItem):
    background: Optional[str]
    foreground: Optional[str]


class StateValue(WorkItem):
    kind: str = PydanticField(default="enum")
    id: str


class StateField(WorkItem):
    type_: str = PydanticField(default="StateIssueCustomField", alias="$type")
    id: str = "130-2"
    value: StateValue


class IssueUpdateRequest(WorkItem):
    fields: List[StateField]
    usesMarkdown: bool = PydanticField(default=True)
    markdownEmbeddings: List = PydanticField(default_factory=list)


class Duration(WorkItem):
    minutes: int
    presentation: Optional[str] = None


class AddSpentTimeRequest(WorkItem):
    duration: Duration
    date: int = PydanticField(default_factory=lambda: int(time.time() * 1000))
    text: Optional[str] = PydanticField(default=None, alias="description")

    model_config = {"arbitrary_types_allowed": True}


class RecentIssueRequest(WorkItem):
    date: int = PydanticField(default_factory=lambda: int(time.time() * 1000))
    issue: Issue

    model_config = {"arbitrary_types_allowed": True}


class IssueFieldNames(StrEnum):
    STATE = "State"
    PRIORITY = "Priority"
    TYPE = "Type"
    ASSIGNEE = "Assignee"
    FIX_VERSIONS = "Fix versions"
    AFFECTED_VERSIONS = "Affected versions"
    FIXED_IN_BUILD = "Fixed in build"
    ESTIMATION = "Estimation"
    SPENT_TIME = "Spent time"


class BundleEnums:
    STATE = "110-0"
    TYPE = "108-1"
    CATEGORY = "108-269"
    FIX_VERSIONS = "113-23"
    PROJECT_ID = "108-35"
    SUBSYSTEMS = "132-7"
    RESOLUTION = "108-198"
    BUILD_NUMBER = "133-1"
    PRIORITY = "108-0"
