import json
import binmay

if __name__ == '__main__':
    binmay.login()

    period = binmay.choose_period()
    score = binmay.view_score(period)

    print(json.dumps(score, indent=4))
