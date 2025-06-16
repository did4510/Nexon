"""Add missing models for macros, maintenance, AI config and staff duty."""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade():
    # Create response_macros table
    op.create_table(
        'response_macros',
        sa.Column('macro_id', sa.String(36), primary_key=True),
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('guilds.guild_id')),
        sa.Column('name', sa.String(100)),
        sa.Column('content', sa.Text),
        sa.Column('category', sa.String(100)),
        sa.Column('created_by', sa.String(20)),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('last_edited_by', sa.String(20)),
        sa.Column('last_edited_at', sa.DateTime, onupdate=datetime.utcnow),
        sa.Column('usage_count', sa.Integer, default=0)
    )

    # Create maintenance_schedules table
    op.create_table(
        'maintenance_schedules',
        sa.Column('schedule_id', sa.String(36), primary_key=True),
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('guilds.guild_id')),
        sa.Column('start_time', sa.DateTime),
        sa.Column('end_time', sa.DateTime),
        sa.Column('description', sa.Text),
        sa.Column('created_by', sa.String(20)),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('notify_users', sa.Boolean, default=True),
        sa.Column('affected_services', sa.JSON)
    )

    # Create ai_configs table
    op.create_table(
        'ai_configs',
        sa.Column('config_id', sa.String(36), primary_key=True),
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('guilds.guild_id')),
        sa.Column('model_name', sa.String(100), default='gpt-3.5-turbo'),
        sa.Column('temperature', sa.Float, default=0.7),
        sa.Column('max_tokens', sa.Integer, default=150),
        sa.Column('enabled_features', sa.JSON),
        sa.Column('custom_prompt', sa.Text),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=datetime.utcnow),
        sa.Column('api_key', sa.String(100)),
        sa.Column('usage_limit', sa.Integer, default=1000),
        sa.Column('current_usage', sa.Integer, default=0)
    )

    # Create staff_duties table
    op.create_table(
        'staff_duties',
        sa.Column('staff_id', sa.String(20), primary_key=True),
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('guilds.guild_id'), primary_key=True),
        sa.Column('started_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('ended_at', sa.DateTime, nullable=True),
        sa.Column('is_on_duty', sa.Boolean, default=True)
    )

def downgrade():
    op.drop_table('staff_duties')
    op.drop_table('ai_configs')
    op.drop_table('maintenance_schedules')
    op.drop_table('response_macros') 