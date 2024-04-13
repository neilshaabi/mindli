from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.models.conversation import Conversation
from app.models.enums import UserRole
from app.models.message import Message
from app.utils.formatters import format_time_since

bp = Blueprint(
    "messages",
    __name__,
)


@bp.route("/messages", methods=["GET"])
@login_required
def messages_entry():
    # Determine field for current user's id based on their role
    if current_user.role == UserRole.THERAPIST:
        current_user_id_field = Conversation.therapist_user_id
    else:
        current_user_id_field = Conversation.client_user_id

    # Create a subquery to fetch the latest message timestamp in each conversation
    latest_message_subquery = (
        db.select(
            Message.conversation_id.label("conversation_id"),
            db.func.max(Message.timestamp).label("latest_timestamp"),
        )
        .group_by(Message.conversation_id)
        .subquery()
    )

    # Fetch the latest conversation by joining with the latest message subquery
    latest_conversation_query = (
        db.select(Conversation)
        .join(
            latest_message_subquery,
            Conversation.id == latest_message_subquery.c.conversation_id,
        )
        .where(current_user_id_field == current_user.id)
        .order_by(latest_message_subquery.c.latest_timestamp.desc())
        .limit(1)
    )
    latest_conversation = db.session.execute(
        latest_conversation_query
    ).scalar_one_or_none()

    # Redirect to endpoint with most recent conversation selected, if one exists
    if latest_conversation is not None:
        return redirect(
            url_for("messages.messages", conversation_id=latest_conversation.id)
        )

    # No conversations found for this user
    else:
        return render_template(
            "messages.html",
            conversations=None,
            messages=None,
        )


@bp.route("/messages/<int:conversation_id>", methods=["GET"])
@login_required
def messages(conversation_id):
    # Determine conversation fields based on the current user's role
    if current_user.role == UserRole.THERAPIST:
        current_user_id_field = Conversation.therapist_user_id
        other_user_field = "client_user"
    elif current_user.role == UserRole.CLIENT:
        current_user_id_field = Conversation.client_user_id
        other_user_field = "therapist_user"

    # Ensure the conversation exists and the current user is part of it
    selected_conversation = db.session.execute(
        db.select(Conversation).filter_by(id=conversation_id)
    ).scalar_one_or_none()
    if not selected_conversation or (
        current_user.id
        not in [
            selected_conversation.therapist_user_id,
            selected_conversation.client_user_id,
        ]
    ):
        return redirect(url_for("messages.messages_entry"))
    else:
        selected_conversation.other_user = getattr(
            selected_conversation, other_user_field
        )

    # Create a subquery to fetch the latest message in each conversation
    latest_message_subquery = (
        db.select(
            Message.conversation_id.label("conversation_id"),
            db.func.max(Message.timestamp).label("latest_timestamp"),
        )
        .group_by(Message.conversation_id)
        .subquery()
    )

    # Fetch conversations using subquery to order conversations by latest message timestamp
    conversations_query = (
        db.select(Conversation)
        .join(
            latest_message_subquery,
            Conversation.id == latest_message_subquery.c.conversation_id,
        )
        .where(current_user_id_field == current_user.id)
        .order_by(latest_message_subquery.c.latest_timestamp.desc())
    )
    conversations = db.session.execute(conversations_query).unique().scalars().all()

    # Display latest message and the time that has passed for each conversation
    for conversation in conversations:
        if conversation.messages:
            latest_message = conversation.messages[-1]
            conversation.latest_message_content = latest_message.content
            conversation.time_since_latest_message = format_time_since(
                latest_message.timestamp
            )
            conversation.other_user = getattr(conversation, other_user_field)

    return render_template(
        "messages.html",
        selected_conversation=selected_conversation,
        conversations=conversations,
    )
