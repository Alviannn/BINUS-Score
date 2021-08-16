import os
import binmay
from colorama import Fore

if __name__ == '__main__':
    os.system('cls')

    print(f'{Fore.GREEN}Logging in to BINUSMaya...{Fore.RESET}')
    binmay.login()

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
