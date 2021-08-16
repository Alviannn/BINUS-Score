import json
import binmay

if __name__ == '__main__':
    print('Logging in to BINUSMaya...')
    binmay.login()

    period = binmay.choose_period()
    score_list = binmay.view_score(period)

    table_line = '+----+------------------------------------------+-------+-------+'
    header_format = '| %-2s | %-40s | %-5s | %-5s |'
    row_format = '| %2d | %-40s | %5s | %-5s |'

    print(table_line)
    print(header_format % ('No', 'Course Name', 'Score', 'Grade'))
    print(table_line)

    count = 0
    for tmp in score_list:
        count += 1
        print(row_format % (count, tmp['course'], str(tmp['final-score']), tmp['grade']))

    print(table_line)
