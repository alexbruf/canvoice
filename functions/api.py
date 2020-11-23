# this module should 
from canvasapi import Canvas
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
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
              limit=10):
    '''
    gets the todo items from the start_date to the end_date
    start_date: datetime (default now)
    end_date: datetime (default 7 days from now)
    start: int (default 0)
    limit: int (default 10)
    '''
    active_courses = self.canvas.get_user('self').get_courses(enrollment_state='active')
    convert_to_context_code = lambda course: 'course_' + str(course.id)

    context_codes = [convert_to_context_code(course) for course in list(active_courses)]
    res = list(self.canvas.get_user('self')
                .get_calendar_events_for_user(context_codes=context_codes,
                                                  start_date=start_date,
                                                  type='assignment',
                                                  end_date=end_date))
    if len(res) == 0:
      return []
    
    return res[start:limit]


  def get_course_grades(self,
                        courses=None):
    '''
    Gets the current grade for specified course(s)
      courses: int[] (default None), course IDs
    Returns array of grade dicts w/ courseID, name, and grade
    '''
    # TODO: Find way to filter classes from this semester (170 is hardcoded for Fall 2020)
    # Build map from courseID to name
    courseNameMap = {}
    user_courses = self.canvas.get_user('self').get_courses()
    for course in user_courses:
      if hasattr(course, 'access_restricted_by_date') or course.enrollment_term_id != 170:
        continue
      courseNameMap[course.id] = course.name

    enrollments = self.canvas.get_user('self').get_enrollments(enrollment_term_id=170)
    grades = []
    for enrollment in enrollments:
      if courses is not None and enrollment.course_id not in courses:
        continue
      gradeObj = {
        'id': enrollment.course_id,
        'name': courseNameMap[enrollment.course_id],
        'score': enrollment.grades['current_score'],
      }
      grades.append(gradeObj)

    return grades

  def get_closest_files(self,
                        file_name,
                        class_name):
    '''
    Gets closest matches to given file_name for files in class with name class_name
      file_name: string, name of desired file
      class_name: string, name of class with file
    Returns list of file objects
    '''
    # Find course the user is asking about
    courses = self.canvas.get_user('self').get_courses(enrollment_state='active')
    class_scores = []
    for c in courses:
      score = fuzz.token_set_ratio(class_name.lower(), str(c.course_code.lower()))
      class_scores.append(score)

    # Returns the index of *one of* of the maximum values, but I guess we have no way to break ties
    course = courses[class_scores.index(max(class_scores))]

    # Calculate token_set_ratio scores for all file names
    class_files = list(course.get_files())
    if len(class_files) == 0:
      return "", 0

    scores = []
    for class_file in class_files:
      score = fuzz.token_set_ratio(file_name.lower(), str(class_file).lower())
      scores.append(score)

    # Find and return top 3 guesses
    best_files = []
    bound = min(3, len(scores))
    for i in range(bound):
      max_idx = scores.index(max(scores))
      best_files.append(class_files[max_idx])
      scores.pop(max_idx)
      class_files.pop(max_idx)

    return best_files, course.id

  

  

  