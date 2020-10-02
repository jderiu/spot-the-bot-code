from templates.src.scoring_utils import get_leaderboard as retrieve_leaderboard, compute_scores_for_user
from flask import jsonify, request


def get_leaderboard():
    return jsonify(retrieve_leaderboard())

def get_score_for_user():
    user_name = request.args.get('user_name', None)
    final_score, avg_corr, avg_turn_penalty = compute_scores_for_user(user_name)
    ret_dict = {
        'final_score': final_score,
        'avg_corr': avg_corr,
        'avg_turn_penalty': avg_turn_penalty
    }
    return jsonify(ret_dict)

routes = [{'url': '/api/get_leaderboard',
           'name': 'get_leaderboard',
           'fn': get_leaderboard,
           'methods': ['GET']},
          {'url': '/api/get_score_for_user',
           'name': 'get_score_for_user',
           'fn': get_score_for_user,
           'methods': ['GET']},
          ]
