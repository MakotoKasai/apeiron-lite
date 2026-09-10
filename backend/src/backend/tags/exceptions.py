# タグ：操作の失敗を表す業務例外。



class TagAlreadyExistsError(Exception):
    pass

class ProjectTagAlreadyExistsError(Exception):
    pass

class NoteTagAlreadyExistsError(Exception):
    pass

class PhotoTagAlreadyExistsError(Exception):
    pass

class TagDoesNotExistsError(Exception):
    pass
class InvalidTagInputError(Exception):
    pass
