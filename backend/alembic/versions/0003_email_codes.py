"""email_codes — passwordless OTP

Revision ID: 0003_email_codes
Revises: 0002_consent_paid
Create Date: 2026-06-29

Таблица одноразовых кодов входа по e-mail (passwordless / OTP). Храним только
bcrypt-хэш кода, TTL и счётчик попыток — см. app/models/email_code.py.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_email_codes"
down_revision = "0002_consent_paid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("code_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_email_codes_email", "email_codes", ["email"])


def downgrade() -> None:
    op.drop_index("ix_email_codes_email", table_name="email_codes")
    op.drop_table("email_codes")
