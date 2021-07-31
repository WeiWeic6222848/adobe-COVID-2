from flask import *
from flask_login import LoginManager, login_user, login_required, \
    logout_user, current_user
from User import User, Course, Lesson, PDF
from Config import Config
import os
import os.path as path
import uuid
import subprocess
from zipfile import ZipFile
from werkzeug.utils import secure_filename
from shutil import rmtree

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = '0QK7SG[NEfVCBsemC$%3qQ.l^*(lB2JsT(*c;npx6dzm,fz,' \
                 'ioHOD]`dhkO,Ibd '
userDB = dict()
coursesDB = dict()
pdfDB = dict()


def resetCourses():
    """
    small helper function which clears the courseDB.
    :return: void
    """
    coursesDB.clear()


def initializeCourses():
    """
    a function that initializes the courseDB based on the folder structure
    found in root folder :return: void
    """
    # get all items in the path
    dirpath = path.join(".", "static", "Courses")
    allitems = os.listdir(dirpath)

    # seperate course directories
    dirs = [path.join(dirpath, f) for f in allitems if
            path.isdir(path.join(dirpath, f))]
    t = coursesDB
    # recursive call for each subdirectories
    for course in dirs:
        tmpCourseObject = Course()
        tmpLessons = [path.join(course, f) for f in os.listdir(course) if
                      path.isdir(path.join(course, f))]
        for lesson in tmpLessons:
            tmpLessonObject = Lesson()
            tmpPdfs = [f for f in os.listdir(lesson) if
                       path.isfile(path.join(lesson, f)) and f[-4:] == ".pdf"]
            for pdf in tmpPdfs:
                tmpPdf = PDF()
                tmpPdf.identifier = path.basename(pdf)
                tmpPdf.uuid = str(
                    uuid.uuid3(uuid.NAMESPACE_DNS, path.join(lesson, pdf)))
                pdfDB[tmpPdf.uuid] = tmpPdf
                tmpLessonObject.pdfs.append(tmpPdf)
            tmpLessonObject.identifier = path.basename(lesson)
            tmpCourseObject.lessons.append(tmpLessonObject)
        tmpCourseObject.identifier = path.basename(course)
        coursesDB[tmpCourseObject.identifier] = tmpCourseObject


initializeCourses()


@login_manager.user_loader
def load_user(userid):
    """
    login manager callback
    :param userid: user id
    :return: found user or nothing.
    """
    return userDB.get(userid, None)


@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    login manager callback
    :return: if user not logged in, send them back to login
    """
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    courses = list(coursesDB.values())
    return render_template('index.html', courses=courses)


@app.route('/creative/')
@login_required
def creative():
    return render_template('creative.html')


@app.route('/saveCreative/', methods=['POST'])
@login_required
def saveCreative():
    # retrieve data
    img = request.form.get('data', None)
    if not img:
        error = 'No image was provided'
        return error, 400

    # create the temporary file
    dirname = path.join(".", 'creatives', current_user.email)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    tempfilename = path.join(dirname, 'index.html')
    temporaryFile = open(tempfilename, "w")

    # write html code, center the image captured
    writeString = "<!DOCTYPE html><html lang=\"en\"><head><meta " \
                  "charset=\"UTF-8\"><title>Creative " \
                  "Corner</title></head><body><img src='{0}' alt='Your " \
                  "Whiteboard Image' style=\"margin: 0 " \
                  "auto;display:block\"></body></html> ".format(img)
    temporaryFile.write(writeString)
    temporaryFile.close()

    zippath = path.join(dirname, 'creative.zip')

    # remove old zip if exist
    if path.isfile(zippath):
        os.remove(zippath)

    # zip the temporary file
    zipObj = ZipFile(zippath, 'w')
    zipObj.write(tempfilename, arcname="index.html")
    zipObj.close()

    outputpath = path.join(dirname, 'output.pdf')

    # call subprocess
    args = ['node', path.join('.', 'pdf_creator', 'bin', 'pdf_creator.js'),
            zippath, outputpath]
    process = subprocess.Popen(args)
    process.wait()

    # return statuc
    if (path.isfile(outputpath)):
        return "success", 200
    else:
        return "failed", 500


@app.route('/downloadCreative/')
@login_required
def downloadCreative():
    # search temporary file
    dirname = path.join(".", 'creatives', current_user.email)
    outputpath = path.join(dirname, 'output.pdf')
    if (path.isfile(outputpath)):
        # sent to download
        return send_from_directory(dirname, 'output.pdf', as_attachment=True)
    else:
        # if there are no temporary file, redirect to creative.
        return redirect(url_for('creative'))


@app.route('/courses/<string:courseName>')
@login_required
def coursePage(courseName):
    # retrieve course information
    course = coursesDB.get(courseName, None)
    if course:
        # if course information is found, render the template with the
        # course information.
        tmp = coursesDB[courseName].todict()
        return render_template('information.html', Course=tmp,
                               AdobeID=Config['AdobeClientID'],
                               GoogleID=Config['GoogleTrackerID'],
                               CommentUpdateInterval=Config[
                                   'CommentUpdateInterval'],
                               ReadPageInterval=Config['ReadingPageInterval'])
    else:
        # else send back to home
        return redirect(url_for('index'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # if the current user is logged in,
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        # check formdata
        email = request.form.get('email', None)
        password = request.form.get('pass', None)
        if not (email and password):
            error = 'the informations given wasn\'t correct!'

        # check user
        user = load_user(email)
        if not user:
            error = 'user not found!'

        # if everything is fine
        if not error:
            if user.password == password:
                # Login and validate the user.
                # user should be an instance of your `User` class
                login_user(user)
                return redirect(url_for('index'))
            else:
                error = 'the given password is incorrect!'

    return render_template('login.html', error=error)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # if the current user is logged in,
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        # check if everything is neatly filled
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        name = request.form.get('name', None)
        number = request.form.get('student_number', None)
        role = request.form.get('role', None)
        role = int(role)  # convert to int if it's a string

        if not (number and name and email and password):
            error = 'the informations given wasn\'t correct!'
            return error, 400
        if userDB.get(email, None):
            error = 'That email has already been registered!'
            return error, 400

        # create user and add it into the db
        user = User(email, password, number, name, role)
        userDB[email] = user
        return 'success', 200
    else:
        return render_template('register.html', error=error,
                               GoogleID=Config['GoogleTrackerID'])


@app.route("/logout/", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/courses/', methods=['POST'])
@login_required
def LoadPDF():
    # check formdata
    course = request.form.get('course', None)
    lesson = request.form.get('lesson', None)
    pdf = request.form.get('pdf', None)

    # find pdf in local space
    if (course and lesson and pdf):
        filepath = path.join('.', 'static', 'Courses', course, lesson, pdf)
        course = coursesDB.get(course, None)
        # find pdf in database
        pdfobj = None
        if course:
            lesson = course.findLesson(lesson)
            if lesson:
                pdfobj = lesson.findPDF(pdf)
        if not pdfobj:
            error = 'Can\'t find the requested pdf!'
            return error, 400
        # if both are okay load comment and return it
        if path.isfile(filepath):
            f = open(filepath, 'rb')
            if f:
                # load comments in the pdf.
                annotations = list(pdfobj.annotations.values())
                responds = {'data': annotations}
                return jsonify(responds)
        else:
            error = 'Can\'t find the requested pdf!'
            return error, 400
    else:
        error = 'Incomeplete request information'
        return error, 400


@app.route('/annotation/', methods=['POST'])
@login_required
def UpdateAnnotation():
    # check annotation exists
    annotation = request.get_json()
    if annotation:
        # upload the annotation on the pdf object
        source = annotation.get("belongsToPDF", None)

        error = 'corrupted annotation data!'
        if not source:
            return error, 400
        creator = annotation.get("creator", None)
        if not creator:
            return error, 400
        creatorname = creator.get("name", None)
        if not creatorname:
            return error, 400

        # check current user is the same as creator
        if current_user.name != creatorname:
            error = 'different user'
            return error, 403

        # add/delete the annotation to the pdf
        pdf = pdfDB.get(source, None)
        annotation['locallystored'] = True  # custom tag.
        if annotation.get('deleting', False):
            pdf.removeAnnotation(annotation)
            return {"result": "deleted", "pdf": pdf.identifier,
                    "annotation": annotation, "email": current_user.email}
        else:
            pdf.addAnnotation(annotation)
            return {"result": "added", "pdf": pdf.identifier,
                    "annotation": annotation, "email": current_user.email}
    else:
        error = 'Incomeplete request information'
        return error, 400


@app.route('/newAnnotation/', methods=['POST'])
@login_required
def GetAnnotation():
    # check uuid exists
    uuid = request.form.get('uuid', None)
    if not uuid:
        error = 'Incomplete request information'
        return error, 400

    # check pdf exists
    pdf = pdfDB.get(uuid, None)
    if not pdf:
        error = 'can\'t find the pdf required'
        return error, 400

    # return the current annotations
    annotations = list(pdf.annotations.values())
    return {'data': annotations}


@app.route('/whiteboard/', methods=['post'])
@login_required
def GetWhiteBoard():
    # get course
    course = request.form.get('course', None)
    if not course:
        error = 'Incomplete request information'
        return error, 400

    # get current users whiteboard annotation for that course
    annotations = current_user.whiteBoardAnnotations.get(course, None)

    # if user doesn't have any annotation, return an empty array
    if not annotations:
        return {'data': {}}

    # else return annotations
    annotations = list(annotations.values())
    return {'data': annotations}


@app.route('/whiteboardAnnotation/', methods=['post'])
@login_required
def UpdateWhiteBoardAnnotation():
    # similar to update annotaion.
    annotation = request.get_json()
    if annotation:
        error = 'corrupted annotation data!'
        creator = annotation.get("creator", None)
        if not creator:
            return error, 400
        creatorname = creator.get("name", None)
        if not creatorname:
            return error, 400
        course = annotation.get("course", None)
        if not course:
            return error, 400
        if current_user.name != creatorname:
            error = 'different user'
            return error, 403
        annotation['locallystored'] = True  # custom tag.

        if annotation.get('deleting', False):
            current_user.removeWhiteBoardComment(course, annotation)
            return {"result": "deleted",
                    "annotation": annotation, "email": current_user.email}
        else:
            current_user.addWhiteBoardComment(course, annotation)
            return {"result": "added",
                    "annotation": annotation, "email": current_user.email}
    else:
        error = 'Incomeplete request information'
        return error, 400


@app.route('/newWhiteboardAnnotation/', methods=['POST'])
@login_required
def GetWhiteboardAnnotation():
    # similar to get annotation
    course = request.form.get('course', None)
    if not course:
        error = 'Incomplete request information'
        return error, 400
    whiteboard = current_user.whiteBoardAnnotations.get(course, None)
    if not whiteboard:
        return {'data': {}}
    annotations = list(whiteboard.values())
    return {'data': annotations}


@app.route('/newCourse/', methods=['POST'])
@login_required
def newCoures():
    # check permission
    if current_user.role != 2:
        error = "permission denialed"
        return error, 403

    # check course existance
    courseName = request.form.get('courseName', None)
    if not courseName:
        error = 'Incomplete request information'
        return error, 400
    if coursesDB.get(courseName, None):
        error = 'Course exists'
        return error, 400

    # if course folder exists, reload the structure.
    if path.isdir(path.join('.', 'static', 'Courses', courseName)):
        resetCourses()
        initializeCourses()
    else:
        # else create the folder and add it to db.
        os.makedirs(path.join('.', 'static', 'Courses', courseName),
                    exist_ok=True)
        newCourseobj = Course()
        newCourseobj.identifier = courseName
        coursesDB[courseName] = newCourseobj
    return "success", 200


@app.route('/newLesson/', methods=['POST'])
@login_required
def newLesson():
    # check permission
    if current_user.role != 2:
        error = "permission denialed"
        return error, 403
    courseName = request.form.get('course', None)
    lessonName = request.form.get('lessonName', None)

    # check existances
    if not (lessonName and courseName):
        error = 'Incomplete request information'
        return error, 400
    coursePath = path.join('.', 'static', 'Courses', courseName)
    if not coursesDB.get(courseName, None) or not path.isdir(coursePath):
        error = 'Course doesn\'t exist'
        return error, 400

    # rebuild if folder exist, otherwise create
    lessonPath = path.join(coursePath, lessonName)
    if path.isdir(lessonPath):
        resetCourses()
        initializeCourses()
    else:
        newLessonObj = Lesson()
        newLessonObj.identifier = lessonName
        coursesDB[courseName].lessons.append(newLessonObj)
        os.makedirs(lessonPath, exist_ok=True)
    return "success", 200


@app.route('/newPDF/', methods=['POST'])
@login_required
def newPDF():
    # check permission
    if current_user.role != 2:
        error = 'permission denialed'
        return error, 403
    pdf = request.files.get('file', None)
    courseName = request.form.get('course', None)
    lessonName = request.form.get('lesson', None)

    # check existances
    if not (lessonName and courseName and pdf):
        error = 'Incomplete request information'
        return error, 400
    pdfName = secure_filename(pdf.filename)
    coursePath = path.join('.', 'static', 'Courses', courseName)
    if not coursesDB.get(courseName, None) or not path.isdir(coursePath):
        error = 'Course doesn\'t exist'
        return error, 400
    courseObj = coursesDB[courseName]
    lessonPath = path.join(coursePath, lessonName)
    if not courseObj.findLesson(lessonName) or not path.isdir(lessonPath):
        error = 'Lesson doesn\'t exist'
        return error, 400
    lessonObj = courseObj.findLesson(lessonName)
    pdfPath = path.join(lessonPath, pdfName)

    # if exists, prompt an error, otherwise save file locally.
    if path.isfile(pdfPath):
        error = 'pdf with that name already exists'
        return error, 400
    else:
        newPDFObj = PDF()
        newPDFObj.identifier = pdfName
        newPDFObj.uuid = uuid.uuid3(uuid.NAMESPACE_DNS, pdfPath)
        pdfDB[str(newPDFObj.uuid)] = newPDFObj
        lessonObj.addPDF(newPDFObj)
        pdf.save(path.join(lessonPath, pdfName))
    return "success", 200


@app.route('/deleteCourse/', methods=['POST'])
@login_required
def delCourse():
    # check permission
    if current_user.role != 2:
        error = "permission denialed"
        return error, 403
    courseName = request.form.get('course', None)

    # check existance
    if not courseName:
        error = 'Incomplete request information'
        return error, 400

    # attempt to delete
    coursepath = path.join('.', 'static', 'Courses', courseName)
    coursesDB.pop(courseName, None)
    rmtree(coursepath, ignore_errors=True)
    return "success", 200


@app.route('/deleteLesson/', methods=['POST'])
@login_required
def delLesson():
    # check permission
    if current_user.role != 2:
        error = "permission denialed"
        return error, 403

    # check existance
    courseName = request.form.get('course', None)
    lessonName = request.form.get('lesson', None)
    if not (courseName and lessonName):
        error = 'Incomplete request information'
        return error, 400
    coursePath = path.join('.', 'static', 'Courses', courseName)
    if not coursesDB.get(courseName, None) or not path.isdir(coursePath):
        error = 'Course doesn\'t exist'
        return error, 400

    # attempt to delete
    lessonPath = path.join(coursePath, lessonName)
    coursesDB[courseName].removeLesson(lessonName)
    rmtree(lessonPath, ignore_errors=True)
    return "success", 200


@app.route('/deletePDF/', methods=['POST'])
@login_required
def delPDF():
    # check permission
    if current_user.role != 2:
        error = "permission denialed"
        return error, 403

    # check existance
    courseName = request.form.get('course', None)
    lessonName = request.form.get('lesson', None)
    pdfName = request.form.get('pdf', None)
    uuid = request.form.get('uuid', None)
    if not (courseName and lessonName and pdfName and uuid):
        error = 'Incomplete request information'
        return error, 400
    coursePath = path.join('.', 'static', 'Courses', courseName)
    couseObj = coursesDB.get(courseName, None)
    if not couseObj or not path.isdir(coursePath):
        error = 'Course doesn\'t exist'
        return error, 400
    lessonPath = path.join(coursePath, lessonName)
    lessonObj = couseObj.findLesson(lessonName)
    if not lessonObj or not path.isdir(lessonPath):
        error = 'Lesson doesn\'t exist'
        return error, 400

    # attempt to delete
    pdfPath = path.join(lessonPath, pdfName)
    lessonObj.removePDF(pdfName)
    pdfDB.pop(uuid, None)
    if path.isfile(pdfPath):
        os.remove(pdfPath)
    return "success", 200


@app.route('/favicon.ico')
def icon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(host='localhost', port=8080)
