# @bp.route("/profile/client", methods=["POST"])
# @login_required
# @client_required
# def client_profile():
#     # Generate form for client-specific information
#     form = ClientProfileForm()

#     # Invalid form submission - return errors
#     if not form.validate_on_submit():
#         return jsonify({"success": False, "errors": form.errors})

#     # Convert form's default values to None
#     if form.preferred_gender.data == "":
#         form.preferred_gender.data = None
#     if form.preferred_language.data == 0:
#         form.preferred_language.data = None

#     client = current_user.client

#     # Update client's profile if it exists
#     if client:
#         client.preferred_gender = form.preferred_gender.data
#         client.preferred_language_id = form.preferred_language.data

#     # Insert new data if no profile exists
#     else:
#         client = Client(
#             user_id=current_user.id,
#             preferred_gender=form.preferred_gender.data,
#             preferred_language_id=form.preferred_language.data,
#         )
#         db.session.add(client)
#     db.session.commit()

#     # Update client's issues
#     form.issues.update_association_data(parent=client, child=Issue, children="issues")

#     db.session.commit()

#     # Reload page
#     flash("Client preferences updated")
#     return jsonify(
#         {
#             "success": True,
#             "url": url_for("profile.profile"),
#         }
#     )
