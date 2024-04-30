from datetime import datetime

from flask import (
    Blueprint,
    Response,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.forms.messages import SendMessageForm
from app.models.conversation import Conversation
from app.models.enums import UserRole
from app.models.message import Message
from app.utils.formatters import format_time_since

bp = Blueprint("messages", __name__, url_prefix="/messages")


@bp.route("/", methods=["GET"])
@login_required
def index():
    # Dynamically choose the criteria to filter conversations depending on user's role
    if current_user.role == UserRole.THERAPIST:
        filter_criteria = Conversation.therapist_user_id == current_user.id
    elif current_user.role == UserRole.CLIENT:
        filter_criteria = Conversation.client_user_id == current_user.id

    # Fetch conversations that have messages
    conversations_with_messages = (
        db.session.execute(
            db.select(Conversation)
            .join(Message)
            .where(filter_criteria)
            .group_by(Conversation.id)
            .order_by(db.func.max(Message.timestamp).desc())
        )
        .scalars()
        .all()
    )

    # Fetch conversations without messages
    conversations_without_messages = (
        db.session.execute(
            db.select(Conversation)
            .where(filter_criteria)
            .outerjoin(Message)
            .having(db.func.count(Message.id) == 0)
            .group_by(Conversation.id)
        )
        .scalars()
        .all()
    )

    # Combine the lists: new conversations first
    conversations = conversations_without_messages + conversations_with_messages

    for conversation in conversations:
        # Store latest message and time for menu bar
        if conversation.messages:
            latest_message = conversation.messages[-1]
            conversation.latest_message_content = latest_message.content
            conversation.time_since_latest_message = format_time_since(
                latest_message.timestamp
            )

        # Handle new conversations with no messages
        else:
            conversation.latest_message_content = "Start a new conversation"
            conversation.time_since_latest_message = ""

        # Initialise form to send messages to this conversation
        conversation.form = SendMessageForm(
            prefix=str(conversation.id),
            id=f"send-message-{conversation.id}",
            endpoint=url_for("messages.send", conversation_id=conversation.id),
        )

    # Render template with conversation from request selected as default
    return render_template(
        "messages.html",
        active_page="messages",
        default_section=request.args.get("section"),
        conversations=conversations,
    )


@bp.route("/<int:therapist_user_id>/<int:client_user_id>", methods=["GET"])
@login_required
def conversation(therapist_user_id: int, client_user_id: int) -> Response:
    # Check user roles and set the correct user_id fields based on the role
    if (
        current_user.role == UserRole.THERAPIST and current_user.id != therapist_user_id
    ) or (current_user.role == UserRole.CLIENT and current_user.id != client_user_id):
        abort(403)

    # Check for an existing conversation between the therapist and client
    conversation = db.session.execute(
        db.select(Conversation).filter_by(
            therapist_user_id=therapist_user_id, client_user_id=client_user_id
        )
    ).scalar_one_or_none()

    # If conversation does not exist, create a new one
    if not conversation:
        conversation = Conversation(
            therapist_user_id=therapist_user_id, client_user_id=client_user_id
        )
        db.session.add(conversation)
        db.session.commit()

    # Redirect to the new conversation after creation
    return redirect(url_for("messages.index", section=conversation.id))


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
        timestamp=datetime.now(),
    )
    db.session.add(message)
    db.session.commit()
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "messages.index",
                conversation_id=conversation_id,
                section=conversation_id,
            ),
        }
    )
