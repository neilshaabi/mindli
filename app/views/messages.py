from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app import db
from app.models.conversation import Conversation
from app.models.enums import UserRole
from app.models.message import Message

bp = Blueprint(
    "messages",
    __name__,
)


@bp.route("/messages", methods=["GET"])
@login_required
def messages():
    # Determine conversation fields based on the current user's role
    if current_user.role == UserRole.THERAPIST:
        current_user_field = Conversation.therapist_user_id
        other_user_field = Conversation.client_user_id
    elif current_user.role == UserRole.CLIENT:
        current_user_field = Conversation.client_user_id
        other_user_field = Conversation.therapist_user_id

    # Create a subquery for the latest message in each conversation
    latest_message_subquery = (
        db.select(
            Message.conversation_id,
            func.max(Message.timestamp).label("latest_timestamp"),
        )
        .group_by(Message.conversation_id)
        .subquery()
    )

    # Fetch conversations using subquery to order conversations by latest message timestamp
    conversations = (
        db.session.execute(
            db.select(Conversation)
            .join(
                latest_message_subquery,
                Conversation.id == latest_message_subquery.c.conversation_id,
            )
            .options(joinedload(Conversation.messages))
            .filter(current_user_field == current_user.id)
            .order_by(latest_message_subquery.c.latest_timestamp.desc())
        )
        .scalars()
        .all()
    )

    # Display latest message of each conversation in template
    for conversation in conversations:
        conversation.latest_message = (
            conversation.messages[-1].content
            if conversation.messages
            else "No messages yet"
        )
        conversation.other_user_full_name = (
            getattr(conversation, other_user_field).first_name
            + " "
            + getattr(conversation, other_user_field).last_name
        )

    return render_template(
        "messages.html", conversations=conversations, other_user_field=other_user_field
    )
