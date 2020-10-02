from flask import render_template, Blueprint, request
hello_blueprint = Blueprint('hello',__name__)

@hello_blueprint.route('/')
@hello_blueprint.route('/hello')
def index():
	return render_template("index.html", convo_id=0, pkg_id=0, show_leaderboard=False, full_convo=False, segmented=False)

@hello_blueprint.route('/rd')
def conditional_index():
	convo_id = request.args.get('id', 0)
	return render_template("index.html", convo_id=convo_id, pkg_id=0, show_leaderboard=False, full_convo=False, segmented=False)

@hello_blueprint.route('/rdfull')
def conditional_index_full():
	convo_id = request.args.get('id', 0)
	return render_template("index.html", convo_id=convo_id, pkg_id=0, show_leaderboard=False, full_convo=True, segmented=False)

@hello_blueprint.route('/pkg')
def packaged_index():
	pkg_id = request.args.get('id', 0)
	return render_template("index.html", convo_id=0, pkg_id=pkg_id, show_leaderboard=False, full_convo=True, segmented=False)


@hello_blueprint.route('/pkgsg')
def packaged_segmented_index():
	pkg_id = request.args.get('id', 0)
	return render_template("index.html", convo_id=0, pkg_id=pkg_id, show_leaderboard=False, full_convo=True, segmented=True)

@hello_blueprint.route('/leaderboard')
def leaderboard():
	return render_template("index.html", convo_id=0, pkg_id=0, show_leaderboard=True, full_convo=False, segmented=False)