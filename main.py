import os
import binmay

from const import LoginError
from colorama import Fore
from time import sleep


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

        header_format = '| %-3s | %-40s | %-5s | %-5s |'
        row_format = '| %3d | %-40s | %5s | %-5s |'

        print('+-----+------------------------------------------+-------+-------+')
        print(header_format % ('No', 'Course Name', 'Score', 'Grade'))
        print('+-----+------------------------------------------+-------+-------+')

        count = 0
        for tmp in score[0]:
            count += 1
            print(row_format % (count, tmp['course'], str(
                tmp['final-score']), tmp['grade']))

        print('+-----+------------------------------------------+-------+-------+')
        print('| %-3s | %-56s |' % ('GPA', str(score[1])))
        print('+-----+----------------------------------------------------------+')

        os.system('pause')


if __name__ == '__main__':
    main()
