# unknown = 0
# student = 1
# teacher = 2


class PDF:
    """
    PDF classes
    """
    identifier = ""  # identifier of PDF object
    uuid = ""  # uuid of object
    annotations = dict()  # dictionary linking annotation id to annotations

    def __init__(self):
        self.identifier = ""
        self.uuid = ""
        self.annotations = dict()

    def addAnnotation(self, annotation):
        """
        add annotation
        :param annotation: annotation as dict
        :return:
        """
        self.annotations[annotation["id"]] = annotation

    def removeAnnotation(self, annotation):
        """
        remove annotation
        :param annotation: annotation as dict
        :return:
        """
        self.annotations.pop(annotation["id"], None)

    def todict(self):
        """
        helper function to create dictionary from object
        :return: dictionary of self, excluding annotations
        """
        mydict = dict()
        mydict["identifier"] = self.identifier
        mydict["uuid"] = self.uuid
        return mydict


class Lesson:
    identifier = ""  # lesson id
    pdfs = list()  # list of pdf links to local storage, just a string.

    def __init__(self):
        self.identifier = ""
        self.pdfs = list()

    def addPDF(self, pdf):
        """
        add pdf
        :param pdf: pdf obj
        :return:
        """
        self.pdfs.append(pdf)
        return

    def removePDF(self, pdf):
        """
        remove pdf
        :param pdf: pdf id
        :return:
        """
        found = self.findPDF(pdf)
        if found:
            self.pdfs.remove(found)
        return

    def findPDF(self, pdfidentifier):
        """
        find pdf
        :param pdfidentifier: pdf id
        :return: pdf obj if exists
        """
        for pdf in self.pdfs:
            if pdf.identifier == pdfidentifier:
                return pdf
        return None

    def todict(self):
        """
        helper function for html
        :return: dictionary of self
        """
        mydict = dict()
        mydict["identifier"] = self.identifier
        mydict["pdfs"] = list()
        for pdf in self.pdfs:
            mydict["pdfs"].append(pdf.todict())
        return mydict


class Course:
    identifier = ""  # course id
    lessons = list()  # list of lesson objects

    def __init__(self):
        self.identifier = ""
        self.lessons = list()
        return

    def addLesson(self, lesson):
        """
        add lesson
        :param lesson: lesson obj
        :return:
        """
        self.lessons.append(lesson)
        return

    def removeLesson(self, id):
        """
        remove lesson
        :param id: lesson id
        :return:
        """
        found = self.findLesson(id)
        if found:
            self.lessons.remove(found)
        return

    def todict(self):
        """
        helper function
        :return: dict of self
        """
        mydict = dict()
        mydict["identifier"] = self.identifier
        mydict["lessons"] = list()
        for lesson in self.lessons:
            mydict["lessons"].append(lesson.todict())
        return mydict

    def findLesson(self, lessonidentifier):
        """
        find lesson
        :param lessonidentifier:  lesson id
        :return: lesson obj if exists
        """
        for lesson in self.lessons:
            if lesson.identifier == lessonidentifier:
                return lesson
        return None


class User:
    email = ""
    password = ""
    number = -1
    name = ""
    whiteBoardAnnotations = dict()  # dictionary[course][anno-id]=annotation
    role = 0  # 1=student,2=teacher
    # callback for flask-login
    auth = False
    is_anonymous = False
    is_active = True

    def __init__(self, email="", password="", number=-1, name="",
                 roles=0):
        self.email = email
        self.password = password
        self.number = number
        self.name = name
        self.role = roles
        self.auth = False
        self.is_anonymous = False
        self.is_active = True
        self.whiteBoardAnnotations = dict()

    def addWhiteBoardComment(self, course, annotation):
        """
        add annotation
        :param course: course id
        :param annotation: annotation obj
        :return:
        """
        if not self.whiteBoardAnnotations.get(course, None):
            self.whiteBoardAnnotations[course] = dict()
        self.whiteBoardAnnotations[course][annotation['id']] = annotation

    def removeWhiteBoardComment(self, course, annotation):
        """
        remove annotation
        :param course: course id
        :param annotation: annotation id
        :return:
        """
        if self.whiteBoardAnnotations.get(course, None):
            self.whiteBoardAnnotations[course].pop(annotation["id"], None)

    # callback for flask login
    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.auth
