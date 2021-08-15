import const
import json
import os
import re
import requests
from typing import List, Union
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
        else:
            print('Successfully logged in!')

    with client.get(f'{const.BINMAY_URL}/newStudent/') as res:
        pass


def choose_period():
    """
    Prompts the user to choose which semester period they want to see their scores.
    NOTE: This function uses some Windows commands such as `cls` and `pause`.

    Returns:
        dict: The selected period object.
    """
    period_list_url = f'{const.BINMAY_URL}/services/ci/index.php/scoring/ViewGrade/getPeriodByBinusianId'

    with client.post(period_list_url, headers=header, data=json.dumps({})) as res:
        periods: dict = res.json()

    # forces user to pick the correct period
    while True:
        os.system('cls')
        try:
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
        period (dict): The period object

    Returns:
        List[dict]: The calculated and graded scores from BINUSMaya
    """
    code: str = period['value']
    score_url = f'{const.BINMAY_URL}/services/ci/index.php/scoring/ViewGrade/getStudentScore/{code}'

    with client.get(score_url, headers=header) as res:
        period_res = res.json()

    score_map = {}
    score_list = period_res['score']
    grading_list = __convert_grading_system(period_res['grading_list'])

    for score_data in score_list:
        course: str = score_data['course']
        score = score_data['score']

        weight: str = score_data['weight']
        weight = weight[:len(weight) - 1]
        weight = float(weight)

        if score == 'N/A':
            score_map[course] = 'N/A'
        if course not in score_map:
            score_map[course] = 0

        if score_map[course] == 'N/A':
            continue

        final_score = (score * weight) / 100
        score_map[course] += final_score

    return __finalize_score(grading_list, score_map)


# ----------------------------- #


def __decide_grade(score: Union[str, float], grading_list: List[dict]):
    """
    Decides based on the score which grade it should be in.
    The grading decision is made by using the `grading_list`.

    Args:
        score: The final calculated score
        grading_list: The grading system which was already been converted to the better version

    Returns:
        str: The decided grade for the provided score (could return 'N/A' if the score is invalid)
    """
    if not isinstance(score, float):
        return 'N/A'

    score = int(score)
    for grading in grading_list:
        score_range = grading['range']

        if score >= score_range[0] and score <= score_range[1]:
            return grading['grade']


def __finalize_score(grading_list: List[dict], score_map: dict):
    """
    Creates the final score with grades to each courses.

    Args:
        grading_list: The grading system which was already been converted to the better version
        score_map: The original score map (generated from the `view_score` function)

    Returns:
        List[dict]: The finalized scores and grades
    """
    graded_scores: List[dict] = []

    for [course, score] in score_map.items():
        res = {
            'course': course,
            'final-score': format(score, '.2f') if isinstance(score, float) else score,
            'grade': __decide_grade(score, grading_list)
        }

        graded_scores.append(res)

    return graded_scores


def __convert_grading_system(grading: List[dict]):
    """
    Converts the grading system (or the object) from BINUS to a better version.

    I need a way to use the grading system easily. Since the original one uses a complete string
    so I thought, why not change it?

    Args:
        grading: the source grading system

    Returns:
        List[dict]: The better version of the grading system.
    """
    better_grading: List[dict] = []

    for grade_obj in grading:
        raw_range_score = str(grade_obj['range']).split(' - ')

        min_range = int(raw_range_score[0])
        max_range = int(raw_range_score[1])

        better_grading.append({
            'grade': grade_obj['grade'],
            'range': (min_range, max_range)
        })

    return better_grading
