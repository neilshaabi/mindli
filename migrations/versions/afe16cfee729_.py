"""empty message

Revision ID: afe16cfee729
Revises: 
Create Date: 2024-02-24 13:57:36.774279

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'afe16cfee729'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('intervention',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('issue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('language',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('iso639_1', sa.String(length=2), nullable=True),
    sa.Column('iso639_2', sa.String(length=3), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('iso639_1'),
    sa.UniqueConstraint('iso639_2'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('date_joined', sa.Date(), nullable=False),
    sa.Column('role', sa.Enum('CLIENT', 'THERAPIST', name='userrole'), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'NON_BINARY', name='gender'), nullable=True),
    sa.Column('photo_url', sa.String(length=255), nullable=True),
    sa.Column('timezone', sa.String(length=50), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)

    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('preferred_gender', sa.Enum('MALE', 'FEMALE', 'NON_BINARY', name='gender'), nullable=True),
    sa.Column('preferred_language_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['preferred_language_id'], ['language.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_user_id'), ['user_id'], unique=False)

    op.create_table('therapist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('country', sa.String(length=50), nullable=False),
    sa.Column('affilitation', sa.Text(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('link', sa.String(length=255), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=True),
    sa.Column('registrations', sa.Text(), nullable=True),
    sa.Column('qualifications', sa.Text(), nullable=True),
    sa.Column('years_of_experience', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('therapist', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_therapist_user_id'), ['user_id'], unique=False)

    op.create_table('availability',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.Column('specific_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('availability', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_availability_therapist_id'), ['therapist_id'], unique=False)

    op.create_table('client_issue',
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('issue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
    sa.PrimaryKeyConstraint('client_id', 'issue_id')
    )
    op.create_table('session_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('session_duration', sa.Integer(), nullable=False),
    sa.Column('fee_amount', sa.Float(), nullable=False),
    sa.Column('fee_currency', sa.String(length=3), nullable=False),
    sa.Column('session_format', sa.Enum('FACE', 'AUDIO', 'VIDEO', name='sessionformat'), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('session_type', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_session_type_therapist_id'), ['therapist_id'], unique=False)

    op.create_table('therapist_format',
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('session_format', sa.Enum('FACE', 'AUDIO', 'VIDEO', name='sessionformat'), nullable=False),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('therapist_id', 'session_format')
    )
    op.create_table('therapist_intervention',
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('intervention_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['intervention_id'], ['intervention.id'], ),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('therapist_id', 'intervention_id')
    )
    op.create_table('therapist_issue',
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('issue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('therapist_id', 'issue_id')
    )
    op.create_table('therapist_language',
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['language.id'], ),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('therapist_id', 'language_id')
    )
    op.create_table('unavailability',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('therapist_id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('unavailability', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_unavailability_therapist_id'), ['therapist_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('unavailability', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_unavailability_therapist_id'))

    op.drop_table('unavailability')
    op.drop_table('therapist_language')
    op.drop_table('therapist_issue')
    op.drop_table('therapist_intervention')
    op.drop_table('therapist_format')
    with op.batch_alter_table('session_type', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_session_type_therapist_id'))

    op.drop_table('session_type')
    op.drop_table('client_issue')
    with op.batch_alter_table('availability', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_availability_therapist_id'))

    op.drop_table('availability')
    with op.batch_alter_table('therapist', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_therapist_user_id'))

    op.drop_table('therapist')
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_user_id'))

    op.drop_table('client')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('language')
    op.drop_table('issue')
    op.drop_table('intervention')
    # ### end Alembic commands ###
