import random


class subject:
    """" Class for the subjects"""

    def __init__(self, name, slots, random_dude):
        self.name = name
        self.slots = slots
        # Decides if a lesson can be taught by a replacement teachers with the wrong degree
        self.random_dude = random_dude
        self.teacher = None
        # active_teacher can be either noone "", teacher or replacement teacher
        self.active_teacher = None

    def set_active_teacher(self, teacher):
        self.active_teacher = teacher


class teacher:
    def __init__(self, name, subject_dict, subjects, subjects_taken, sickliness):
        random.seed(name)
        self.name = name
        self.subjects = subjects
        self.subjects_taken = subjects_taken
        # Every teacher is assigned his subjects slots
        self.slots = [slot for slots in [subject_dict[subject].slots for subject in subjects_taken] for slot in slots]
        if sickliness != -1:
            self.sickliness = sickliness
        else:
            self.sickliness = random.uniform(0, 0.4)
        self.ideal_temperature = 21 + random.uniform(-2, 2)
        # Every teacher is assigned additional slots (not subjects) until they are busy in 15 slots
        self.slots.extend(random.sample([x for x in range(1, 26) if x not in self.slots], 15 - len(self.slots)))
        self.slots.sort()
        self.sick = False

    def set_sick(self):
        if (random.random() < self.sickliness):
            self.sick = True
        else:
            self.sick = False


def get_teacher_data():
    output = dict()
    for key in TEACHER_DICT:
        output.update({key:TEACHER_DICT[key].sick})
    return output


def get_subject_data(slots):
    output = dict()
    for slot in slots:
        subject = slot_to_subject(slot)
        if subject != "":
            output.update({slot:[subject,SUBJECT_DICT[subject].active_teacher]})
    return output


def subjects_to_slots(subject_dict, subjects):
    return [slot for slots in [subject_dict[subject].slots for subject in subjects] for slot in slots]


def slot_to_subject(slot):
    for subject in SUBJECT_DICT:
        if slot in (SUBJECT_DICT[subject].slots):
            return subject
    return ""


SUBJECT_DICT = dict(maths=subject("maths", [1, 21], False), german=subject("german", [2, 7], True),
                    english=subject("english", [3, 11], True), physics=subject("physics", [8, 12], False),
                    informatik=subject("informatik", [16, 22], False), chemistry=subject("chemistry", [17], False),
                    arts=subject("arts", [18], True), geography=subject("geography", [13], False),
                    history=subject("history", [9], False), sports=subject("sports", [10], True))

TEACHER_DICT = dict(
    Mai=teacher("Mai", SUBJECT_DICT, ["maths", "informatik"], ["maths", "informatik"], 0.4),
    Phym=teacher("Phym", SUBJECT_DICT, ["physics", "maths"], ["physics"],-1),
    Kunstler=teacher("Kunstler", SUBJECT_DICT, ["arts"], ["arts"], 0.3),
    Histo=teacher("Histo", SUBJECT_DICT, ["history", "geography"], ["history"],-1),
    Ostih=teacher("Ostih", SUBJECT_DICT, ["history", "geography"], ["geography"],-1),
    Sportler=teacher("Sportler", SUBJECT_DICT, ["sports", "english"], ["sports"], 0.05),
    Denglisch=teacher("Denglisch", SUBJECT_DICT, ["german", "english"], ["german", "english"], 0.7),
    Bio=teacher("Bio", SUBJECT_DICT, ["physics", "chemistry"], ["chemistry"],-1),
    Natur=teacher("Natur", SUBJECT_DICT, ["physics", "maths", "chemistry"], [], 0.1),
    Info=teacher("Info", SUBJECT_DICT, ["informatik"], [],-1))

for teacher in TEACHER_DICT:
    for subject in TEACHER_DICT[teacher].subjects_taken:
        SUBJECT_DICT[subject].teacher = teacher
