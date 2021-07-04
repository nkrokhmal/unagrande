import os.path

from app.imports.runtime import *
from app.main import main


@main.route("/download_boiling_plan", methods=["POST", "GET"])
@flask_login.login_required
def download_boiling_plan():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        "boiling_plan"
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_schedule_plan", methods=["POST", "GET"])
@flask_login.login_required
def download_schedule_plan():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        "schedule"
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_schedule_task", methods=["POST", "GET"])
@flask_login.login_required
def download_schedule_task():
    date = flask.request.args.get("date")
    file_name = flask.request.args.get("file_name")
    uploads = os.path.join(
        os.path.dirname(flask.current_app.root_path),
        flask.current_app.config["DYNAMIC_DIR"],
        date,
        "task"
    )
    response = flask.send_from_directory(
        directory=uploads, filename=file_name, cache_timeout=0, as_attachment=True
    )
    response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
    return response


@main.route("/download_last_schedule_task", defaults={'check_date': False}, methods=["GET", "POST"])
@flask_login.login_required
def download_last_schedule_task(check_date):
    dates = [folder for folder in os.listdir(flask.current_app.config["DYNAMIC_DIR"]) if folder.startswith('20')]
    task_dirs = [os.path.join(
            os.path.dirname(flask.current_app.root_path),
            flask.current_app.config["DYNAMIC_DIR"],
            x,
            "task",
            f"{x}.csv"
        )
        for x in dates]
    task_dirs = [x for x in task_dirs if os.path.exists(x)]
    task_dirs = sorted(task_dirs, reverse=True)
    print(task_dirs)
    if len(task_dirs) > 0:
        last_dir, filename = os.path.split(task_dirs[0])
        print(last_dir)
        print(filename)
        response = flask.send_from_directory(
            directory=last_dir, filename=filename, cache_timeout=0, as_attachment=True
        )
        response.cache_control.max_age = flask.current_app.config["CACHE_FILE_MAX_AGE"]
        return response
    else:
        raise Exception("There is no csv files in schedule task directory!")



