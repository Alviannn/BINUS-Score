from time import sleep
import const
import os
import binmay

from colorama import Fore

def main():
    os.system('cls')
    const.load_config()

    print(f'{Fore.LIGHTGREEN_EX}Logging in to BINUSMaya...{Fore.RESET}')
    try:
        binmay.login()
        print(f'{Fore.LIGHTGREEN_EX}Successfully logged in to BINUSMaya!')
        sleep(2)
    except:
        print(f'{Fore.LIGHTRED_EX}Failed to login to BINUSMaya!')
        os.system('pause')
        return

    print(Fore.RESET)

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
        print(row_format % (count, tmp['course'], str(tmp['final-score']), tmp['grade']))

    print('+-----+------------------------------------------+-------+-------+')
    print('| %-3s | %-56s |' % ('GPA', str(score[1])))
    print('+-----+----------------------------------------------------------+')


if __name__ == '__main__':
    main()