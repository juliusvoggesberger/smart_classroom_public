import school

teach_dict = school.TEACHER_DICT
subject_dict = school.SUBJECT_DICT


def solve_csp(slot, sick_list):
    """solves the indirect csp / classical planning problem for teacher assignment"""
    slot = int(slot)
    lec = school.slot_to_subject(slot)
    teach = subject_dict[lec].teacher
    a = not sick_list[teach]
    if a:
        # initial teacher is available
        changes = False
    else:
        # initial teacher is not available
        changes = True
        a, t = find_affine_teacher(lec, slot, teach_dict, sick_list)
        trivial = subject_dict[lec].random_dude
        if a:
            # affine teacher is available
            teach = t
        elif trivial:
            a, t = find_some_teacher(lec, slot, teach_dict, sick_list)
            if a:
                # some teacher is available
                teach = t
            else:
                # no teacher is available
                teach = ''
        else:
            # no teacher is available
            teach = ''
    return [lec, changes, teach]


def find_affine_teacher(lecture, slot, teacher_dict, sick_list):
    """returns an affine replacement teacher if possible"""
    for t in teacher_dict:
        if lecture in teacher_dict[t].subjects:
            if is_free(t, slot, sick_list):
                return True, t
    return False, ''


def is_free(teach, slot, sick_list):
    """checks if the teacher is able to hold the lesson (is not sick and has no other lecture at this time)"""
    if sick_list[teach] or (slot in teach_dict[teach].slots):
        return False
    return True


def find_some_teacher(lecture, slot, teacher_dict, sick_list):
    """returns some replacement teacher if possible"""
    for t in teacher_dict:
        if lecture not in teacher_dict[t].subjects:
            if is_free(t, slot, sick_list):
                return True, t
    return False, ''
