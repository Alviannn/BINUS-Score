import const
import json
import math
import os
import re
import requests

from typing import List, Tuple, Union
from bs4 import BeautifulSoup


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
    with client.get(f'{const.BINMAY_URL}/login/') as res:
        soup = BeautifulSoup(res.text, const.HTML_PARSER)

    inputs = soup.find_all('input')

    # extracting keys (for the form data)
    user_key = inputs[0]['name']
    pwd_key = inputs[1]['name']
    submit_key = inputs[2]['name']

    csrf_url: str = soup.find_all('script')[4]['src']
    csrf_url = f'{const.BINMAY_URL}{csrf_url[2:len(csrf_url)]}'

    with client.get(csrf_url) as res:
        soup = BeautifulSoup(res.text, const.HTML_PARSER)

    mapped_csrf = re.findall(
        r'name="([^"]+)" .* value="([^"]+)"', soup.prettify())

    extra_payload = {}
    for obj in mapped_csrf:
        extra_payload[obj[0]] = obj[1]

    payload = {
        user_key: const.USERNAME,
        pwd_key: const.PASSWORD,
        submit_key: 'Login'
    }

    payload.update(extra_payload)

    with client.post(f'{const.BINMAY_URL}/login/sys_login.php', data=payload) as res:
        if not res.url.endswith('/newStudent/'):
            raise Exception('Failed to login to BINUSMaya!')

    with client.get(f'{const.BINMAY_URL}/newStudent/') as res:
        pass


def choose_period() -> dict:
    """
    Prompts the user to choose which semester period they want to see their scores.
    NOTE: This function uses some Windows commands such as `cls` and `pause`.

    Returns:
        The selected period object.
    """
    period_list_url = f'{const.BINMAY_URL}/services/ci/index.php/scoring/ViewGrade/getPeriodByBinusianId'

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


def view_score(period: dict) -> Tuple[List[dict], Union[float, str]]:
    """
    Grabs the scores from BINUSMaya then calculate and grade them.

    Args:
        period (dict): The period object

    Returns:
        The calculated and graded scores from BINUSMaya along with the GPA
    """
    code: str = period['value']
    score_url = f'{const.BINMAY_URL}/services/ci/index.php/scoring/ViewGrade/getStudentScore/{code}'

    with client.get(score_url, headers=header) as res:
        period_res = res.json()

    score_map = {}
    score_list = period_res['score']
    # converts the original grading list into a better version
    # it's just a better parsed one
    grading_list = __convert_grading_system(period_res['grading_list'])

    for score_data in score_list:
        course: str = score_data['course']
        score = score_data['score']

        weight: str = score_data['weight']
        weight = weight[:len(weight) - 1]
        weight = float(weight)

        scu: int = score_data['scu']

        # default object value
        score_obj = {
            'scu': scu,
            'score': 0
        }

        if course not in score_map:
            score_map[course] = score_obj

        # score can be invalid, so just set it to that
        # since we're going to skip it later on
        if isinstance(score, str):
            score_map[course]['score'] = score

        # skip course with invalid score
        # since we can't calculate the full score one invalid score
        # therefore, we're just going to keep skipping it
        if score_map[course]['score'] == 'N/A':
            continue

        # updates the calculated score
        final_score = (score * weight) / 100
        score_map[course]['score'] += final_score

    finalized = __finalize_score(grading_list, score_map)
    gpa = __calculate_gpa(finalized, grading_list)

    return (finalized, gpa)


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


def __finalize_score(grading_list: List[dict], score_map: dict) -> List[dict]:
    """
    Creates the final score with grades to each courses.

    Args:
        grading_list: The grading system which was already been converted to the better version
        score_map: The original score map (generated from the `view_score` function)

    Returns:
        The finalized scores and grades
    """
    graded_scores: List[dict] = []

    for [course, obj] in score_map.items():
        score = obj['score']
        final_score = math.ceil(score) if isinstance(score, float) else 'N/A'

        res = {
            'course': course,
            'final-score': final_score,
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
        if score_obj['final-score'] == 'N/A':
            return 'N/A'

        grade_obj = list(filter(lambda g: g['grade'] == score_obj['grade'], grading_list))[0]

        gp = grade_obj['value']
        scu = score_obj['scu']

        gp_sum += (gp * scu)
        total_scu += scu

    gpa: float = gp_sum / total_scu
    last_point = int(format(gpa, '.3f')[-1])

    if last_point == 5:
        gpa += 0.001

    return float(format(gpa, '.2f'))