# ノート：操作の失敗を表す業務例外。


class NoteAlreadyExistsError(Exception):
    pass
class ProjectNoteAlreadyExistsError(Exception):
    pass
class InvalidNoteInputError(Exception):
    pass
class NoteNotFoundError(Exception):
    pass