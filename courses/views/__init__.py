from .catalog import course_list, course_detail, lesson_detail
from .assessment import test_take, test_submit, test_result
from .submissions import assignment_submit
from .manage_dashboard import manage_dashboard
from .manage_courses import (
    course_list_manage, course_manage, course_create, course_edit, course_delete,
    module_create, module_edit, module_delete,
)
from .manage_lessons import lesson_manage, lesson_create, lesson_edit, lesson_delete
from .manage_content import (
    video_create, video_edit, video_delete,
    presentation_create, presentation_edit, presentation_delete,
    material_create, material_edit, material_delete,
)
from .manage_tests import (
    test_create, test_edit, test_delete,
    question_manage, question_create, question_edit, question_delete,
)
from .manage_assignments import assignment_create, assignment_edit, assignment_delete
from .manage_groups import (
    group_list, group_create, group_edit, group_delete,
)
from .grading import grading_list, grade_submission, test_results

__all__ = [
    'course_list', 'course_detail', 'lesson_detail',
    'test_take', 'test_submit', 'test_result',
    'assignment_submit',
    'manage_dashboard',
    'course_list_manage', 'course_manage', 'course_create', 'course_edit', 'course_delete',
    'module_create', 'module_edit', 'module_delete',
    'lesson_manage', 'lesson_create', 'lesson_edit', 'lesson_delete',
    'video_create', 'video_edit', 'video_delete',
    'presentation_create', 'presentation_edit', 'presentation_delete',
    'material_create', 'material_edit', 'material_delete',
    'test_create', 'test_edit', 'test_delete',
    'question_manage', 'question_create', 'question_edit', 'question_delete',
    'assignment_create', 'assignment_edit', 'assignment_delete',
    'group_list', 'group_create', 'group_edit', 'group_delete',
    'grading_list', 'grade_submission', 'test_results',
]
