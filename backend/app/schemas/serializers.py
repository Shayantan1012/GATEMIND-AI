def serialize_profile(profile):
    if not profile:
        return None
    return {
        "profile_id": profile.profile_id,
        "preferred_subjects": profile.preferred_subjects,
        "profile_image": profile.profile_image,
        "headline": profile.headline,
        "bio": profile.bio,
        "college_name": profile.college_name,
        "current_semester": profile.current_semester,
        "graduation_year": profile.graduation_year,
        "daily_study_goal_hours": profile.daily_study_goal_hours,
        "weekly_mock_test_goal": profile.weekly_mock_test_goal,
        "exam_goal_score": profile.exam_goal_score,
        "total_mock_tests": profile.total_mock_tests,
        "weak_subjects": profile.weak_subjects,
        "strong_subjects": profile.strong_subjects,
        "subject_performance": profile.subject_performance,
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


def serialize_mock_test_with_questions(mock_test, questions):
    data = serialize_mock_test(mock_test)
    data["questions"] = [serialize_question(item, include_answer=True) for item in questions]
    return data
