"""Add topics/line_topics: a shallow graph linking Portia's per-scene logical
flaws (PORTIA_LOGICAL_FLAWS) to the play_lines that actually discuss them.

Deliberately scoped to each linked evidence's own (corrected) ftln range,
NOT the whole act/scene — bassanio_plea, blood_reveal, and alien_law_reveal
all sit inside the same 4.1 courtroom scene, so a whole-scene bootstrap would
tag hundreds of unrelated lines under all three topics. That's the same
"irrelevant neighbor dilutes the prompt" failure mode that got the earlier
ftln-radius context experiment in choice_folger_context.py reverted (see
migration 026 / that revert commit) — this migration exists to avoid
repeating it.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "027_add_topic_graph"
down_revision: Union[str, None] = "026_fix_evidence_ftln_ranges"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TOPICS: list[dict[str, str]] = [
    {
        "topic_id": "portia_opens",
        "label": (
            "Portia frames mercy as Shylock's moral obligation, but ignores that "
            "Antonio's party has shown no mercy to Shylock either. The argument "
            "is asymmetric — mercy is demanded of Shylock alone."
        ),
    },
    {
        "topic_id": "bassanio_plea",
        "label": (
            "Bassanio offers ten times the bond and appeals to mercy, but treats "
            "Shylock's lawful contract as something money can simply replace. He "
            "ignores that Shylock was denied dignity long before this trial began."
        ),
    },
    {
        "topic_id": "crowd_jeers",
        "label": (
            "The crowd dehumanizes Shylock based on ethnicity, not conduct. "
            "This is prejudice masquerading as moral judgment."
        ),
    },
    {
        "topic_id": "jessica_attack",
        "label": (
            "Jessica's elopement is a private family matter irrelevant to "
            "contract law. Portia introduces it to emotionally undermine "
            "Shylock, not to make a legal argument."
        ),
    },
    {
        "topic_id": "hath_not_moment",
        "label": (
            "Portia questions whether Shylock has human feeling, yet the court "
            "has systematically denied him the human dignity she demands he "
            "show. The argument is self-contradicting."
        ),
    },
    {
        "topic_id": "blood_reveal",
        "label": (
            "Portia applies extreme literalism to void the bond — interpreting "
            "'flesh' as excluding 'blood' defies the contextual meaning of the "
            "contract. No contract can be executed under such impossible "
            "conditions by design."
        ),
    },
    {
        "topic_id": "alien_law_reveal",
        "label": (
            "The alien law is applied retroactively to punish Shylock for "
            "attempting to enforce a contract the court itself initially "
            "recognized as valid. This is double jeopardy — first voiding the "
            "bond, then criminalizing the attempt."
        ),
    },
]

# topic_id -> [(ftln_start, ftln_end), ...] — verified against the live corpus
# (same anchors used to fix evidence.source_ftln_start/end in migration 026).
_TOPIC_LINE_RANGES: dict[str, list[tuple[int, int]]] = {
    "portia_opens": [(1003158, 1003165)],
    "bassanio_plea": [(4001085, 4001219)],
    "crowd_jeers": [(1003120, 1003140)],
    "jessica_attack": [(2004033, 2004036)],
    "hath_not_moment": [(3001057, 3001066)],
    "blood_reveal": [(4001339, 4001340), (4001319, 4001321)],
    "alien_law_reveal": [(4001363, 4001369)],
}


def upgrade() -> None:
    conn = op.get_bind()

    op.create_table(
        "topics",
        sa.Column("topic_id", sa.String(64), primary_key=True),
        sa.Column("label", sa.Text, nullable=False),
    )
    op.create_table(
        "line_topics",
        sa.Column("ftln", sa.Integer, sa.ForeignKey("play_lines.ftln"), primary_key=True),
        sa.Column("topic_id", sa.String(64), sa.ForeignKey("topics.topic_id"), primary_key=True),
    )

    conn.execute(
        sa.text("INSERT INTO topics (topic_id, label) VALUES (:topic_id, :label)"),
        _TOPICS,
    )

    for topic_id, ranges in _TOPIC_LINE_RANGES.items():
        for start, end in ranges:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO line_topics (ftln, topic_id)
                    SELECT ftln, :topic_id FROM play_lines
                    WHERE ftln BETWEEN :start AND :end
                    ON CONFLICT DO NOTHING
                    """
                ),
                {"topic_id": topic_id, "start": start, "end": end},
            )


def downgrade() -> None:
    op.drop_table("line_topics")
    op.drop_table("topics")
