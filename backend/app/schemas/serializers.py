def serialize_profile(profile):
    if not profile:
        return None
    return {
        "profile_id": profile.profile_id,
        "preferred_subject": profile.preferred_subject,
        "profile_image": profile.profile_image,
        "overall_progress": profile.overall_progress,
        "performance_percentage": profile.performance_percentage,
        "preparation_progress": profile.preparation_progress,
        "mock_test_history": profile.mock_test_history,
    }


def serialize_user(user):
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "branch": user.branch.value,
        "target_gate_year": user.target_gate_year,
        "is_email_verified": user.is_email_verified,
        "account_status": user.account_status.value,
        "profile": serialize_profile(user.user_profile),
    }


def serialize_admin(admin):
    return {
        "admin_id": admin.admin_id,
        "full_name": admin.full_name,
        "email": admin.email,
        "phone_number": admin.phone_number,
        "role": admin.role.value,
        "account_status": admin.account_status.value,
        "is_verified": admin.is_verified,
    }


def serialize_question(question, include_answer=False):
    data = question.to_dict()
    data["question_id"] = data.pop("_id")
    data["created_at"] = data["created_at"].isoformat()
    if not include_answer:
        data.pop("correct_answer", None)
        data.pop("explanation", None)
    return data


def serialize_mock_test(mock_test):
    data = mock_test.to_dict()
    data["mock_test_id"] = data.pop("_id")
    data["created_at"] = data["created_at"].isoformat()
    return data
