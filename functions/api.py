# this module should 
from canvasapi import Canvas
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz, process

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
    gets the to-do items from the start_date to the end_date
    start_date: datetime (default now)
    end_date: datetime (default 7 days from now)
    start: int (default 0)
    limit: int (default 10)
    course: str (default None)
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
    #for c in user_courses:
    #  print(c)
    for nextCourse in user_courses:
      if hasattr(nextCourse, 'access_restricted_by_date'):# or nextCourse.enrollment_term_id != 170:
        continue
      courseNameMap[nextCourse.id] = nextCourse.name
      courseCodeMap[nextCourse.id] = nextCourse.course_code

    # If course was specified, find the closest match
    courseCode = None
    if course:
      courseCode = process.extractOne(course, [*courseCodeMap.values()])[0]

    enrollments = self.canvas.get_user('self').get_enrollments()#enrollment_term_id=170)
    grades = []
    for enrollment in enrollments:
      #print(enrollment.course_id)
      if course and courseCodeMap[enrollment.course_id] != courseCode:
        continue
      try:
        gradeObj = {
          'code': courseCodeMap[enrollment.course_id],
          'name': courseNameMap[enrollment.course_id],
          'score': enrollment.grades['current_score'],
        }
      except:
        continue
      grades.append(gradeObj)
      #print(grades)

    return grades


  def get_closest_files(self,
                        file_name,
                        class_name,
                        prev_found):
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
      score = fuzz.token_set_ratio(class_name.lower(), str(c.course_code).lower())
      class_scores.append(score)

    # Returns the index of *one of* of the maximum values, but I guess we have no way to break ties
    course = courses[class_scores.index(max(class_scores))]

    # Calculate token_set_ratio scores for all file names
    class_files = list(course.get_files())
    if len(class_files) == 0:
      return "", 0

    scores = []
    for class_file in class_files:
      # Skip file if it was picked in previous attempt
      if (prev_found is not None) and str(class_file.id) in prev_found:
        continue
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


  def fetch_file_to_send(self,
                         course_id,
                         file_id):
    '''
    Temporarily downloads file with id file_id and fetches user's email 
      file_id: string, id of desired file
      course_id: string, id of relevant course
    Returns user's email and file's name 
    ''' 
    user = self.canvas.get_user('self')
    course = self.canvas.get_course(course_id)
    file = course.get_file(file_id)

    profile = user.get_profile()
    url = file.url
    download_idx = url.find("download")
    url_filtered = url[:download_idx]

    # Returns user's primary email and the file name 
    return profile["primary_email"], url_filtered 


  def get_filtered_announcements(self,
                        start_date=datetime.now() - timedelta(days=7),
                        end_date=datetime.now(),
                        start=0,
                        limit=10,
                        course=None):
    '''
    gets announcements from the start_date to the end_date
    start_date: datetime (default now)
    end_date: datetime (default 7 days from now)
    start: int (default 0)
    limit: int (default 10)
    course: str (default None)
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
    contextCodeMap = {}
    for nextCourse in list(active_courses):
      if course and nextCourse.course_code != courseCode:
        continue
      context_code = convert_to_context_code(nextCourse)
      context_codes.append(context_code)
      contextCodeMap[context_code] = nextCourse.course_code.split()[0] + ' ' + nextCourse.course_code.split()[1]
    res = list(self.canvas.get_announcements(context_codes=context_codes,
                                             start_date=start_date,
                                             end_date=end_date))
    if len(res) == 0:
      return [], {}

    return res[start:limit], contextCodeMap


  def get_assignment_info(self, class_name, assignment_name):
    """
    Finds closest matching assignment and returns grading info on it, if any exists
      class_name: string, class name provided by user
      assignment_name: string, assignment name provided by user 
    Returns assignemntInfo object containing user's score, possible points, and letter grade if any exist 
    """
    # Find course the user is asking about
    user = self.canvas.get_user('self')
    courses = user.get_courses(enrollment_state='active')
    class_scores = []
    for c in courses:
      score = fuzz.token_set_ratio(class_name.lower(), str(c.course_code).lower())
      class_scores.append(score)

    # Returns the index of *one of* of the maximum values, but I guess we have no way to break ties
    course = courses[class_scores.index(max(class_scores))]
    
    # Find assignment user is asking about 
    assignments = user.get_assignments(course.id)

    assn_scores = []
    for assn in assignments:
      score = fuzz.token_set_ratio(assignment_name.lower(), str(assn.name).lower())
      assn_scores.append(score)

    assn = assignments[assn_scores.index(max(assn_scores))]

    try:
      name = assn.name
      score = assn.get_submission('self').score
      pts_poss = assn.points_possible
      grade = ""
      grade = str(round((float(score) / float(pts_poss)) * 100, 3) ) + "%"
    except:
      print("No score found for " + name)
      return {"score" : "", "name" : name}

    assn_obj = {
      "score" : str(round(float(score), 3)),
      "points_possible" : pts_poss,
      "grade" : grade,
      "name" : name
    }
    
    return assn_obj

  def get_syllabus(self, class_name):
    courses = self.canvas.get_user('self').get_courses(enrollment_state='active')
    class_scores = []
    for c in courses:
      score = fuzz.token_set_ratio(class_name.lower(), str(c.course_code).lower())
      class_scores.append(score)

    # Returns the index of *one of* of the maximum values, but I guess we have no way to break ties
    course = courses[class_scores.index(max(class_scores))]

    # Find file name closest to syllabus
    class_files = list(course.get_files())
    if len(class_files) == 0:
      return "", 0

    scores = []
    for class_file in class_files:
      score = fuzz.token_set_ratio("syllabus", str(class_file).lower())
      scores.append(score)

    syllabus = class_files[scores.index(max(scores))]
    return syllabus.get_contents()

