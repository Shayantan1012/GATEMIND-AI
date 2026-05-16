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
