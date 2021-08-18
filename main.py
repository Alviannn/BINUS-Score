import binmay
import os

from ascii_table import *
from const import LoginError
from colorama import Fore
from time import sleep
from typing import Any, Dict, Union


def print_calculated_scores(score_list: List[dict], gpa: Union[float, str]):
    table = Table([
        TableColHeader('No', 3, True),
        TableColHeader('Course Name', 40),
        TableColHeader('Score', 5, True),
        TableColHeader('Grade', 5)
    ])

    count = 0
    for tmp in score_list:
        count += 1
        table.add_row([str(count), tmp['course'], str(tmp['final_score']), str(tmp['grade'])])

    table.print_table()

    print('| %-3s | %-56s |' % ('GPA', str(gpa)))
    print('+-----+----------------------------------------------------------+')


def print_score_map(score_map: Dict[str, Any]):
    count = 0
    for [course_name, course_obj] in score_map.items():
        count += 1

        print(f'{count}. {course_name} ({course_obj["scu"]} SCU):')
        for [key, data] in course_obj.items():
            if key == 'scu':
                continue

            key = ' - '.join(key.split(': '))
            print(f'    * {key}: {data["score"]} ({data["weight"]}%)')

        print()

def main():
    while True:
        os.system('cls')
        print(f'{Fore.LIGHTGREEN_EX}Logging in to BINUSMaya...{Fore.RESET}')
        try:
            binmay.login()

            print(f'{Fore.LIGHTGREEN_EX}Successfully logged in to BINUSMaya!')
            print(Fore.RESET)

            sleep(2)
        except LoginError as ex:
            if ex.code == LoginError.SCRAPE_FAIL:
                print(
                    f'{Fore.LIGHTRED_EX}Failed to scrape BINUSMaya!\n'
                    'Possible cause:\n'
                    f'{Fore.LIGHTYELLOW_EX}* {Fore.LIGHTRED_EX}The website could be under maintenance, visit the site to make sure!\n'
                    f'{Fore.LIGHTYELLOW_EX}* {Fore.LIGHTRED_EX}Your internet might be down, check your internet connection!')
            elif ex.code == LoginError.INCORRECT_CREDENTIALS:
                print(
                    f'{Fore.LIGHTRED_EX}Incorrect username or password! Please check it again!')
            elif ex.code == LoginError.UNKNOWN:
                print(
                    f'{Fore.LIGHTRED_EX}An unknown error has occurred that causes the program to fail to login!'
                    'Please contact the developer!')

            print(Fore.RESET)
            os.system('pause')
            # repeat until success... somehow...
            continue

        # if success then break the loop
        break

    while True:
        period = binmay.choose_period()
        score = binmay.view_score(period)

        print_score_map(score['score_map'])
        print_calculated_scores(score['score_list'], score['gpa'])

        os.system('pause')


if __name__ == '__main__':
    main()
