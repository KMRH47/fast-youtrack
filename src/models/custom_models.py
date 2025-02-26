from typing import List
from models.general_responses import Issue, Link


class CustomIssue(Issue):
    links: List[Link]
