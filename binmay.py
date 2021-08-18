import json
import math
import os
import re
import requests
import stdiomask

from const import *
from bs4 import BeautifulSoup
from typing import List, Union

# ----------------------------- #

header = {
    'user-agent': 'Mozilla/5.0',
    'host': 'binusmaya.binus.ac.id',
    'referer': 'https://binusmaya.binus.ac.id/newStudent/'
}

client = requests.session()

# ----------------------------- #


def login():
    """
    Login to BINUSMaya with the credentials provided at .env file

    Raises:
        Exception: Thrown if program failed to login to BINUSMaya
    """
    try:
        with client.get(f'{BINMAY_URL}/login/') as res:
            soup = BeautifulSoup(res.text, HTML_PARSER)
            inputs = soup.find_all('input')

        # extracting keys (for the form data)
        user_key: str = inputs[0]['name']
        pwd_key: str = inputs[1]['name']
        submit_key: str = inputs[2]['name']

        csrf_url: str = soup.find_all('script')[4]['src']
        csrf_url = f'{BINMAY_URL}{csrf_url[2:len(csrf_url)]}'

        with client.get(csrf_url) as res:
            soup = BeautifulSoup(res.text, HTML_PARSER)

        mapped_csrf = re.findall(
            r'name="([^"]+)" .* value="([^"]+)"', soup.prettify())
    except:
        raise LoginError(LoginError.SCRAPE_FAIL)

    # ask for username and password to BINUSMaya
    username = input('Your BINUS username (without \'@binus.ac.id\'): ')
    password = stdiomask.getpass('Your BINUS password: ')

    # make the payload / formdata
    payload = {
        user_key: username,
        pwd_key: password,
        submit_key: 'Login'
    }

    # add extra key-values from the CSRF url
    for obj in mapped_csrf:
        payload[obj[0]] = obj[1]

    with client.post(f'{BINMAY_URL}/login/sys_login.php', data=payload) as res:
        if 'login/?error' in res.url:
            raise LoginError(LoginError.INCORRECT_CREDENTIALS)
        elif 'newStudent' not in res.url:
            raise LoginError(LoginError.UNKNOWN)

    with client.get(f'{BINMAY_URL}/newStudent/') as res:
        pass


def choose_period() -> dict:
    """
    Prompts the user to choose which semester period they want to see their scores.
    NOTE: This function uses some Windows commands such as `cls` and `pause`.

    Returns:
        The selected period object.
    """
    period_list_url = f'{BINMAY_URL}/services/ci/index.php/scoring/ViewGrade/getPeriodByBinusianId'

    with client.post(period_list_url, headers=header, data=json.dumps({})) as res:
        periods: dict = res.json()

    # forces user to pick the correct period
    while True:
        os.system('cls')
        try:
            print('Available Semester Periods')
            print()

            count = 0
            for period in periods:
                count += 1
                print(f'{count}. {period["field"]}')

            print()
            choice = int(input(f'Choose: '))
            assert 1 <= choice <= len(periods)

            return periods[choice - 1]
        except Exception:
            print('Invalid choice!')
            os.system('pause')


def view_score(period: dict):
    """
    Grabs the scores from BINUSMaya then calculate and grade them.

    Args:
        period: The period object

    Returns:
        The calculated and graded scores from BINUSMaya along with the GPA
    """
    code: str = period['value']
    score_url = f'{BINMAY_URL}/services/ci/index.php/scoring/ViewGrade/getStudentScore/{code}'

    with client.get(score_url, headers=header) as res:
        period_res = res.json()

    calculated_scores = {}
    full_score_map = {}

    score_list = period_res['score']
    # converts the original grading list into a better version
    # it's just a better parsed one
    grading_list = __convert_grading_system(period_res['grading_list'])

    for score_data in score_list:
        course_name: str = score_data['course']
        score: Union[int, str] = score_data['score']
        weight = float(score_data['weight'][:-1])
        scu: int = score_data['scu']
        lam: str = score_data['lam']

        # default object for calculated scores
        calculated_score_obj = {
            'scu': scu,
            'score': 0
        }

        if course_name not in calculated_scores:
            calculated_scores[course_name] = calculated_score_obj
        if course_name not in full_score_map:
            full_score_map[course_name] = { 'scu': scu }

        full_score_map[course_name][lam] = {
            'weight': weight,
            'score': score
        }

        # score can be invalid (N/A), so just set it to that
        # since we're going to skip it later on
        if isinstance(score, str):
            calculated_scores[course_name]['score'] = score

        # skip course with invalid score
        # since we can't calculate the full score if we have at least one invalid score
        # therefore, we're just going to keep skipping it
        if calculated_scores[course_name]['score'] == 'N/A':
            continue

        # updates the calculated score
        final_score = (score * weight) / 100
        calculated_scores[course_name]['score'] += final_score

    finalized = __finalize_score(grading_list, calculated_scores)
    gpa = __calculate_gpa(finalized, grading_list)

    return { 'score_list': finalized, 'gpa': gpa, 'score_map': full_score_map }


# ----------------------------- #


def __decide_grade(score: Union[str, int], grading_list: List[dict]) -> str:
    """
    Decides based on the score which grade it should be in.
    The grading decision is made by using the `grading_list`.

    Args:
        score: The final calculated score (could be N/A)
        grading_list: The grading system which was already been converted to the better version

    Returns:
        The decided grade for the provided score (could return 'N/A' if the score is invalid)
    """
    if isinstance(score, str):
        return 'N/A'

    for grading in grading_list:
        score_range = grading['range']

        if score >= score_range[0] and score <= score_range[1]:
            return grading['grade']


def __finalize_score(grading_list: List[dict], calculated_score: dict) -> List[dict]:
    """
    Creates the final score with grades to each courses.

    Args:
        grading_list: The grading system which was already been converted to the better version
        calculated_score: The calculated final score (generated from `view_score` and it's not actually final)

    Returns:
        The finalized scores and grades
    """
    graded_scores: List[dict] = []

    for [course, obj] in calculated_score.items():
        score = obj['score']
        final_score = math.ceil(score) if isinstance(score, float) else 'N/A'

        res = {
            'course': course,
            'final_score': final_score,
            'grade': __decide_grade(final_score, grading_list),
            'scu': obj['scu']
        }

        graded_scores.append(res)

    return graded_scores


def __convert_grading_system(raw_grading: List[dict]) -> List[dict]:
    """
    Converts the original grading system (or the object) from BINUS to a better version.

    I need a way to use the grading system easily. Since the original one uses a complete string
    so I thought, why not change it?

    Basically, this just converts the score range value from string to integer and changed the 'descr' key to 'value'

    Args:
        raw_grading: the source grading system

    Returns:
        The better version of the grading system.
    """
    better_grading: List[dict] = []

    for grade_obj in raw_grading:
        raw_range = str(grade_obj['range']).split(' - ')

        min_range = int(raw_range[0])
        max_range = int(raw_range[1])

        better_grading.append({
            'grade': grade_obj['grade'],
            'range': (min_range, max_range),
            'value': grade_obj['descr']
        })

    return better_grading


def __calculate_gpa(graded_scores: List[dict], grading_list: List[dict]) -> Union[float, str]:
    """
    Calculates the GPA based on your grades.

    Args:
        graded_scores: The finalized and graded scores
        grading_list: The (better version) grading system

    Returns:
        The calculated GPA, could be `str` if there are any invalid score (N/A), otherwise `float`
    """
    gp_sum = 0
    total_scu = 0

    for score_obj in graded_scores:
        if score_obj['final_score'] == 'N/A':
            return 'N/A'

        grade_obj = list(
            filter(lambda g: g['grade'] == score_obj['grade'], grading_list))[0]

        gp = grade_obj['value']
        scu = score_obj['scu']

        gp_sum += (gp * scu)
        total_scu += scu

    gpa: float = gp_sum / total_scu
    last_point = int(format(gpa, '.3f')[-1])

    if last_point == 5:
        gpa += 0.001

    return float(format(gpa, '.2f'))
