# 写真：操作の失敗を表す業務例外。


class PhotoAlreadyExistsError(Exception):
    pass
class PhotoDoesNotExistsError(Exception):
    pass
class ProjectPhotoAlreadyExistsError(Exception):
    pass
class NotePhotoAlreadyExistsError(Exception):
    pass
class NotePhotoDoesNotExistsError(Exception):
    pass
class InvalidPhotoInputError(Exception):
    pass