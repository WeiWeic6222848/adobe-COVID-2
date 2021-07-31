#ADOBE-USECASE-2
demo video link: https://youtu.be/AAXBMKolLrk

This project is built for topcoder challenge Adobe-usecase-2.
It is a collaboration website for teachers and students, where student and 
teachers can add comments/annotations to existing courses and pdfs.

The projects folder contains the folders
```
creatives
pdf_creator
static
templates
```
- creatives: temporary folder for the pdf_creator to output the pdf file.
- pdf_creator: npm based commandline tool that utilizes the PDF Tool API.
- static: static server-side resources for the website
- templates: jinja2 templates for python flask

The root folder has:
```
app.py
Config.py
readme.md
requirements.txt
User.py
```
- app.py: core python flask application.
- Config.py: configurable variables for app.py
- readme.md: this file
- requirements.txt: frozen requirement for python flask
- User.py: utility classes for the app.py

#requirements
- python3
- nodejs
- npm

#Installation/setup
##Website
make sure you have the newest version of nodejs and npm and python
```
https://nodejs.org/
https://www.npmjs.com/
https://www.python.org/downloads/
```

install the requirements via 
```
pip3 install -r requirements.txt
```

in the Config.py, change the Tracker-ID and Adobe-ID to your own.
```
Config = {
->  "AdobeClientID": "401ce579a51d4f8382bb714dd0483ef4",
->  "GoogleTrackerID": "UA-172415720-3",
    "CommentUpdateInterval": 3000  # millisecond
    "ReadingPageInterval": 10000, #milliseconds, if the user stayed longer than this interval on one page, then the user has read that page.
}
```
keep in mind it's domain restricted.

in the Config.py, adjust the interval which the comments are going to be updated,
also, adjust the interval which you consider a user will need to be able to read a pdf page.
```
Config = {
    "AdobeClientID": "401ce579a51d4f8382bb714dd0483ef4",
    "GoogleTrackerID": "UA-172415720-3",
->  "CommentUpdateInterval": 3000  # millisecond
->  "ReadingPageInterval": 10000, #milliseconds, if the user stayed longer than this interval on one page, then the user has read that page.
}
```

##pdf_creator

inside the folder `pdf_creator`:

overwrite the `dc-services-sdk-credentials.json` and `private.key` inside `pdf_creator` with your own.

then, execute the following command

```
npm install
npm link (optional)
```

#Execution
ensure the internet connection is stable and execute following in the project root folder

```
python3 app.py
```

the website should be deployed under `localhost:8080`

##Setting up google Analytics dashboard
there're in total 3 google analytics dashboard template I created:
- Introduction Dashboard:
features total pageview, realtime user, Total registrations,
average values and student assignment completions...,
it contains the most useful information.

```
https://analytics.google.com/analytics/web/template?uid=nC3iCqMMS3qKG9jKSL0aXA
```
- PDF-Lesson-Course Dashboard 1: it features print, comment usage and time spent information for the top-9 PDF,Courses and Lesson. 

The print, comment usage and time spent information of Courses and Lessons are the sum of the information from the pdf which belongs to the course/lesson.
```
https://analytics.google.com/analytics/web/template?uid=3qYyFuihSNep1HmDfdXTYg
```

- PDF-Lesson-Course Dashboard 2: it features opened, page view, page read and download information for the top-9 PDF,Courses and Lesson. 

The opened, page read/view and download information of Courses and Lessons are the sum of the information from the pdf which belongs to the course/lesson.
```
https://analytics.google.com/analytics/web/template?uid=Lz2zPV2XTmOCvLOQK-OlbA
```

####Tracked events:
```
DOCUMENT_OPEN
COURSE_DOCUMENT_OPEN
LESSON_DOCUMENT_OPEN
PAGE_VIEW
COURSE_PAGE_VIEW
LESSON_PAGE_VIEW
DOCUMENT_DOWNLOAD
COURSE_DOCUMENT_DOWNLOAD
LESSON_DOCUMENT_DOWNLOAD
DOCUMENT_PRINT
COURSE_DOCUMENT_PRINT
LESSON_DOCUMENT_PRINT
COMMENT_ADDED
COURSE_COMMENT_ADDED
LESSON_COMMENT_ADDED
TOOL_USED
COMMENT_DELETED
COURSE_COMMENT_DELETED
LESSON_COMMENT_DELETED
STUDENT_WEBSITE_TIME_SPENT
COURSE_TIME_SPENT
PAGE_READ
COURSE_PAGE_READ
LESSON_PAGE_READ
TOTAL_PAGE_VIEW
TOTAL_PAGE_READ
TOTAL_PDF_TIME_SPENT
ASSIGNMENT_COMPLETE
STUDENT_ASSIGNMENT_COMPLETE
REGISTERED
```
##Brief Introduction
- Login-page and Registration is clear to itself.

- Once you login using the created credentials, you can see all the available courses,
you can click on any of them to navigate to respective course page.

- On the course page, there're lessons and their respective pdfs if it exists on the server side.

- Clicking on the pdf links will open full screen pdf viewer, the users can freely add any annotation/comments, they will be 
uploaded to server side and distributed to other people.

- **Whenever a user annotates 'complete' in any of the pdf, the student will complete the 'assignment' of that pdf.**

- each user has a unique whiteboard for each courses, they can keep a note on anything they want and save them for later.

- user can use the save button from pdf viewer to download the comment/annotations in whiteboard/pdfs.

**PDF TOOL USAGE:**
- **On the creative page which can be found in the header navigation area. you can freely draw within the canvas.
Whenever you click on save, your drawing will be converted into a image which the server will be saving into a html file,
and converting into a pdf using pdf tool API. the resulting PDF will be sent directly to the user.**

- Users with a role of teacher will get to see more options/buttons on the home page and the course page, 
they can add/remove courses, lesson and pdf at will, but the google analytics event which already has been registered won't disappear.

- The courses, lessons and pdfs are persisted to the projects folder. they will not be lost after a reboot, however, the comments will be lost.

###Known issue
- PDF viewer sometime will not be fit-width although it is set to fit-width.

- User will be able to see the delete/edit button for the comment of other people, however, 
if they do use the feature, and server refused it, a comment update will be triggered directly,
causing the updated comment to revert to it's original state almost immediately,
 which doesn't interrupt the seamless experience.

- When updating the color and the width of the shape, it will not be seamlessly
updated for the other user, as the API doesn't support updating anything other than
the bodyValue of a comment/annotation as stated in the documentation(ref. https://www.adobe.com/devnet-docs/dcsdk_io/viewSDK/howtos_comments.html#annotations-interface in `updateAnnotation API`).

- When drawing a shape on pdf, there is a rare occasion where the shape's selector 
will not be valid, when the server saved this shape, the clients will keep updating it
and it will keep failing. however, this doesn't affect the other comments/annotations.

- Creative corner only work with desktop (with mouses), as it tracks mouse movements.

- Lighthouse report sometimes gives error on performances while executed on 
desktop mode, it is a known issue and already fixed, 
but it is not published yet (ref.https://github.com/GoogleChrome/lighthouse/issues/11154)

