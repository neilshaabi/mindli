from flask import Blueprint, Response, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.messages import SendMessageForm
from app.models.conversation import Conversation
from app.models.enums import UserRole
from app.models.message import Message
from app.utils.formatters import format_time_since

bp = Blueprint(
    "messages",
    __name__,
    url_prefix="/messages"
)


@bp.route("/", methods=["GET"])
@login_required
def index():
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


    # Fetch conversations using subquery to order conversations by latest message timestamp
    conversations = db.session.execute(db.select(Conversation)
        .join(
            latest_message_subquery,
            Conversation.id == latest_message_subquery.c.conversation_id,
        )
        .where(current_user_id_field == current_user.id)
        .order_by(latest_message_subquery.c.latest_timestamp.desc())).unique().scalars().all()
    

    for conversation in conversations:
        
        # Store latest message and time for menu bar
        if conversation.messages:
            latest_message = conversation.messages[-1]
            conversation.latest_message_content = latest_message.content
            conversation.time_since_latest_message = format_time_since(
                latest_message.timestamp
            )
        
        # Initialise form to send messages to this conversation
        conversation.form = SendMessageForm(prefix=str(conversation.id),
                id=f"send-message-{conversation.id}",
                endpoint=url_for(
                    "messages.send", conversation_id=conversation.id
                ),
            )
    
    # Render template with latest conversation selected as default
    return render_template(
        "messages.html",
        default_section=request.args.get("section", latest_conversation.id),
        conversations=conversations,)


@bp.route("/<int:conversation_id>/update", methods=["POST"])
def send(conversation_id: int) -> Response:
    form = SendMessageForm(prefix=str(conversation_id))

    # Do nothing if form is submitted without any text
    if not form.validate_on_submit():
        return jsonify({"success": True})

    message = Message(
        conversation_id=conversation_id,
        author_id=current_user.id,
        content=form.message.data,
    )
    db.session.add(message)
    db.session.commit()
    return jsonify(
        {
            "success": True,
            "url": url_for("messages.index", conversation_id=conversation_id, section=conversation_id),
        }
    )
