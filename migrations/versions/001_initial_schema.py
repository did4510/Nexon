"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-06-15 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE ticket_status AS ENUM ('open', 'pending_user', 'pending_staff', 'in_progress', 'escalated', 'resolved', 'closed')")
    op.execute("CREATE TYPE participant_role AS ENUM ('creator', 'added_staff', 'added_user')")

    # Create guilds table
    op.create_table(
        'guilds',
        sa.Column('guild_id', sa.String(), primary_key=True),
        sa.Column('support_panel_channel_id', sa.String()),
        sa.Column('support_panel_message_id', sa.String()),
        sa.Column('ticket_parent_category_id', sa.String()),
        sa.Column('ticket_logs_channel_id', sa.String()),
        sa.Column('transcript_logs_channel_id', sa.String()),
        sa.Column('default_staff_role_ids', postgresql.ARRAY(sa.String())),
        sa.Column('admin_role_ids', postgresql.ARRAY(sa.String())),
        sa.Column('escalation_role_id', sa.String()),
        sa.Column('ticket_counter', sa.Integer(), default=0),
        sa.Column('theme_color', sa.String(), default='0x7289DA'),
        sa.Column('maintenance_mode_enabled', sa.Boolean(), default=False),
        sa.Column('maintenance_message', sa.Text()),
        sa.Column('blacklisted_users', postgresql.JSONB()),
        sa.Column('whitelisted_users', postgresql.ARRAY(sa.String())),
        sa.Column('default_language', sa.String(), default='en')
    )

    # Create ticket_categories table
    op.create_table(
        'ticket_categories',
        sa.Column('category_db_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('guild_id', sa.String(), sa.ForeignKey('guilds.guild_id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('emoji', sa.String()),
        sa.Column('staff_role_ids', postgresql.ARRAY(sa.String())),
        sa.Column('modal_fields', postgresql.JSONB()),
        sa.Column('initial_message_template', sa.Text())
    )

    # Create tickets table
    op.create_table(
        'tickets',
        sa.Column('ticket_db_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('ticket_id_display', sa.String(), nullable=False),
        sa.Column('guild_id', sa.String(), sa.ForeignKey('guilds.guild_id')),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('creator_id', sa.String(), nullable=False),
        sa.Column('claimed_by_id', sa.String()),
        sa.Column('status', sa.Enum('open', 'pending_user', 'pending_staff', 'in_progress', 'escalated', 'resolved', 'closed', name='ticket_status')),
        sa.Column('category_db_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ticket_categories.category_db_id')),
        sa.Column('opened_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('last_message_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
        sa.Column('closure_reason_text', sa.Text()),
        sa.Column('closure_reasons_selected', postgresql.JSONB()),
        sa.Column('transcript_url', sa.String()),
        sa.Column('last_staff_response_at', sa.DateTime()),
        sa.Column('last_user_response_at', sa.DateTime()),
        sa.Column('initial_input_data', postgresql.JSONB()),
        sa.Column('internal_notes', postgresql.JSONB()),
        sa.Column('linked_tickets', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('anonymous_mode', sa.Boolean(), default=False),
        sa.Column('sentiment_score_history', postgresql.JSONB()),
        sa.Column('ai_tags', postgresql.ARRAY(sa.String())),
        sa.Column('ai_summary', sa.Text()),
        sa.Column('scheduled_followup_at', sa.DateTime()),
        sa.Column('closed_by_id', sa.String())
    )

    # Create ticket_participants table
    op.create_table(
        'ticket_participants',
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('ticket_db_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tickets.ticket_db_id')),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('creator', 'added_staff', 'added_user', name='participant_role')),
        sa.Column('added_at', sa.DateTime(), default=datetime.utcnow)
    )

    # Create ticket_feedback table
    op.create_table(
        'ticket_feedback',
        sa.Column('feedback_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('ticket_db_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tickets.ticket_db_id')),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('rating', sa.Integer()),
        sa.Column('comments', sa.Text()),
        sa.Column('submitted_at', sa.DateTime(), default=datetime.utcnow)
    )

    # Create staff_performance table
    op.create_table(
        'staff_performance',
        sa.Column('performance_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('guild_id', sa.String(), sa.ForeignKey('guilds.guild_id')),
        sa.Column('staff_id', sa.String(), nullable=False),
        sa.Column('tickets_handled_count', sa.Integer(), default=0),
        sa.Column('avg_response_time_seconds', sa.Float()),
        sa.Column('avg_resolution_time_seconds', sa.Float()),
        sa.Column('last_updated', sa.DateTime(), default=datetime.utcnow),
        sa.Column('on_duty_status', sa.Boolean(), default=False),
        sa.Column('on_duty_since', sa.DateTime())
    )

    # Create sla_definitions table
    op.create_table(
        'sla_definitions',
        sa.Column('sla_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('guild_id', sa.String(), sa.ForeignKey('guilds.guild_id')),
        sa.Column('category_db_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ticket_categories.category_db_id')),
        sa.Column('response_sla_minutes', sa.Integer()),
        sa.Column('resolution_sla_minutes', sa.Integer())
    )

    # Create knowledge_base table
    op.create_table(
        'knowledge_base',
        sa.Column('article_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('guild_id', sa.String(), sa.ForeignKey('guilds.guild_id')),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('keywords', postgresql.ARRAY(sa.String())),
        sa.Column('url', sa.String()),
        sa.Column('category', sa.String()),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('last_edited_by', sa.String()),
        sa.Column('last_edited_at', sa.DateTime())
    )

    # Create macros table
    op.create_table(
        'macros',
        sa.Column('macro_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('guild_id', sa.String(), sa.ForeignKey('guilds.guild_id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('staff_role_ids', postgresql.ARRAY(sa.String()))
    )

    # Create indexes for better query performance
    op.create_index('idx_tickets_guild_id', 'tickets', ['guild_id'])
    op.create_index('idx_tickets_status', 'tickets', ['status'])
    op.create_index('idx_tickets_category', 'tickets', ['category_db_id'])
    op.create_index('idx_tickets_creator', 'tickets', ['creator_id'])
    op.create_index('idx_tickets_claimed_by', 'tickets', ['claimed_by_id'])
    op.create_index('idx_participants_ticket', 'ticket_participants', ['ticket_db_id'])
    op.create_index('idx_participants_user', 'ticket_participants', ['user_id'])
    op.create_index('idx_feedback_ticket', 'ticket_feedback', ['ticket_db_id'])
    op.create_index('idx_staff_perf_guild', 'staff_performance', ['guild_id'])
    op.create_index('idx_staff_perf_staff', 'staff_performance', ['staff_id'])
    op.create_index('idx_kb_guild', 'knowledge_base', ['guild_id'])
    op.create_index('idx_kb_category', 'knowledge_base', ['category'])
    op.create_index('idx_macros_guild', 'macros', ['guild_id'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_macros_guild')
    op.drop_index('idx_kb_category')
    op.drop_index('idx_kb_guild')
    op.drop_index('idx_staff_perf_staff')
    op.drop_index('idx_staff_perf_guild')
    op.drop_index('idx_feedback_ticket')
    op.drop_index('idx_participants_user')
    op.drop_index('idx_participants_ticket')
    op.drop_index('idx_tickets_claimed_by')
    op.drop_index('idx_tickets_creator')
    op.drop_index('idx_tickets_category')
    op.drop_index('idx_tickets_status')
    op.drop_index('idx_tickets_guild_id')

    # Drop tables
    op.drop_table('macros')
    op.drop_table('knowledge_base')
    op.drop_table('sla_definitions')
    op.drop_table('staff_performance')
    op.drop_table('ticket_feedback')
    op.drop_table('ticket_participants')
    op.drop_table('tickets')
    op.drop_table('ticket_categories')
    op.drop_table('guilds')

    # Drop enum types
    op.execute('DROP TYPE participant_role')
    op.execute('DROP TYPE ticket_status')