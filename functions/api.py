# this module should 
from canvasapi import Canvas
from datetime import datetime, timedelta
from fuzzywuzzy import process

API_URL="https://umich.instructure.com"

class CanvasAPI:
  """
  This module connects to the canvas api and
  defines all canvas capabilities and parses results
  of canvas functions
  """

  def __init__(self, api_key):
    self.api_key = api_key
    self.canvas = Canvas(API_URL, self.api_key)


  def get_todo(self, 
              start_date=datetime.now(),
              end_date=datetime.now() + timedelta(days=7),
              start=0,
              limit=10,
              course=None):
    '''
    gets the todo items from the start_date to the end_date
    start_date: datetime (default now)
    end_date: datetime (default 7 days from now)
    start: int (default 0)
    limit: int (default 10)
    '''
    active_courses = self.canvas.get_user('self').get_courses(enrollment_state='active')
    convert_to_context_code = lambda course: 'course_' + str(course.id)

    # If course was specified, find the closest match
    courseCode = None
    if course:
      activeCourseNames = []
      for nextCourse in list(active_courses):
        if hasattr(nextCourse, 'access_restricted_by_date') or nextCourse.enrollment_term_id != 170:
          continue
        activeCourseNames.append(nextCourse.course_code)
      courseCode = process.extractOne(course, activeCourseNames)[0]

    context_codes = []
    for nextCourse in list(active_courses):
      if course and nextCourse.course_code != courseCode:
        continue
      context_codes.append(convert_to_context_code(nextCourse))
    res = list(self.canvas.get_user('self')
                .get_calendar_events_for_user(context_codes=context_codes,
                                                  start_date=start_date,
                                                  type='assignment',
                                                  end_date=end_date))
    if len(res) == 0:
      return []
    
    return res[start:limit]


  def get_course_grades(self,
                        course=None):
    '''
    Gets the current grade for specified course(s)
      course: str (default None), course code
    Returns array of grade dicts w/ courseID, name, and grade
    '''
    # Build map from courseID to name
    courseNameMap = {}
    courseCodeMap = {}
    user_courses = self.canvas.get_user('self').get_courses(enrollment_state='active')
    for nextCourse in user_courses:
      if hasattr(nextCourse, 'access_restricted_by_date') or nextCourse.enrollment_term_id != 170:
        continue
      courseNameMap[nextCourse.id] = nextCourse.name
      courseCodeMap[nextCourse.id] = nextCourse.course_code

    # If course was specified, find the closest match
    courseCode = None
    if course:
      courseCode = process.extractOne(course, [*courseCodeMap.values()])[0]

    enrollments = self.canvas.get_user('self').get_enrollments(enrollment_term_id=170)
    grades = []
    for enrollment in enrollments:
      if course and courseCodeMap[enrollment.course_id] != courseCode:
        continue
      gradeObj = {
        'code': courseCodeMap[enrollment.course_id],
        'name': courseNameMap[enrollment.course_id],
        'score': enrollment.grades['current_score'],
      }
      grades.append(gradeObj)

    return grades