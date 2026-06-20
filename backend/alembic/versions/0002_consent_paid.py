"""consent + per-report paid

Revision ID: 0002_consent_paid
Revises: 0001_init
Create Date: 2026-06-08

Меняем модель:
- подписок нет, тариф пользователя удаляем (users.plan + enum user_plan);
- 152-ФЗ ст. 9: фиксируем факт согласия (consent_at, consent_policy_version);
- добавляем OAuth-провайдера и делаем password_hash nullable
  (OAuth-юзер может не иметь локального пароля);
- разовая оплата привязана к отчёту (scans.paid).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_consent_paid"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users: убираем тариф (подписок больше нет), делаем password_hash nullable,
    # добавляем consent и oauth_provider.
    op.drop_column("users", "plan")
    op.execute("DROP TYPE IF EXISTS user_plan")

    op.alter_column("users", "password_hash", existing_type=sa.String(255), nullable=True)
    op.add_column("users", sa.Column("oauth_provider", sa.String(16), nullable=True))
    op.add_column("users", sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("consent_policy_version", sa.String(16), nullable=True))

    # scans: per-report paid флаг.
    op.add_column(
        "scans",
        sa.Column("paid", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("scans", "paid")

    op.drop_column("users", "consent_policy_version")
    op.drop_column("users", "consent_at")
    op.drop_column("users", "oauth_provider")
    op.alter_column("users", "password_hash", existing_type=sa.String(255), nullable=False)

    user_plan = sa.Enum("free", "pro", "team", name="user_plan")
    user_plan.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("plan", user_plan, nullable=False, server_default="free"),
    )
