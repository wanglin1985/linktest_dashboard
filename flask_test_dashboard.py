#!/usr/bin/python
# coding=utf-8

import collections
import traceback
from functools import wraps

from flask import render_template, redirect, url_for, flash, session, request, jsonify, make_response, abort
from flask_httpauth import HTTPBasicAuth
from markupsafe import Markup
from sqlalchemy import desc


import settings
from dashboard_log import framework_logger
from forms import LoginForm, RegistForm
from modules import ExecutionSummary, db, ExecutionLogs, User, app

auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    print("******************************* get the username: %s" % username)
    print("******************************* get the username: %s" % username)
    print("******************************* get the username: %s" % username)

    print(username)
    print(request)
    user = User.query.filter_by(user_name=username).first()

    if "username" not in session:
        # user = User.query.filter((User.user_name==data["name"])|(User.email==data["name"])).first()

        if user is None:
            return None

        print("*****************--------------************** return the password '%s' for user: '%s' " % (user.password, username))
        return user.password

    else:
        print("*****************--------------************** return the password '%s' for user: '%s' " % (user.password, username))
        return user.password


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/api/v1.0/project_names', methods=['GET'])
@auth.login_required
def get_projects():
    project_names = []

    for row in db.session.query(ExecutionSummary.project_name.distinct().label('project_name')):
        project_names.append(row.project_name)

    if len(project_names) == 0:
        abort(404)
    return jsonify({'project_names': project_names})


@app.route('/projects')
@app.route('/project/<string:projectname>/')
@app.route('/project/<string:projectname>/<int:page>/')
def admin(projectname=None, page=None):
    try:
        if projectname is not None:
            if page is None:
                page = 1
            per_page = 15

            execution_id_count_for_chart = 30
            if hasattr(settings, "execution_id_count"):
                execution_id_count = settings.execution_id_count
            else:
                execution_id_count = 30

            rows_count_for_project = ExecutionSummary.query.filter_by(project_name=projectname).count()
            if rows_count_for_project < 1:
                framework_logger.error("there are no data found for project_name: ", projectname)
                raise BaseException("there are no data found for project_name:", projectname)
            else:
                rows_for_project_in_execution_summary = ExecutionSummary.query.filter_by(
                    project_name=projectname).order_by(desc(ExecutionSummary.execution_id)). \
                    limit(execution_id_count).from_self().paginate(page=page, per_page=per_page)

            execution_id_pass_fail_count_map = {}
            rows = ExecutionSummary.query.filter_by(project_name=projectname).order_by(
                desc(ExecutionSummary.execution_id)).limit(execution_id_count_for_chart).all()  # todo limit config it

            for row in rows:
                execution_id_pass_fail_count_map[row.execution_id] = [row.total_testcases_count,
                                                                      row.pass_testcases_count,
                                                                      row.fail_testcases_count]

                execution_id_pass_fail_count_map = collections.OrderedDict(
                    sorted(execution_id_pass_fail_count_map.items(), reverse=False))

            execution_id_list_for_highcharts = ''
            passed_count_list = ''
            failed_count_list = ''

            for exec_id in execution_id_pass_fail_count_map:
                execution_id_list_for_highcharts += u"'" + "-".join(exec_id.split("-")[0:5]) + u"',"
                passed_count_list += str(execution_id_pass_fail_count_map[exec_id][1]) + ','
                failed_count_list += str(execution_id_pass_fail_count_map[exec_id][2]) + ','

            # execution_id_list_for_dropdown = []
            #
            # rows = ExecutionSummary.query.filter_by(project_name=projectname).limit(30).all()
            # if len(rows) == 0:
            #     execution_id_list_for_dropdown = None
            # else:
            #     print(rows)
            #     for row in rows:
            #         execution_id_list_for_dropdown.append(row.execution_id)
            #         execution_id_list_for_dropdown.sort(reverse=True)

            return render_template("project_summary.html",
                                   execution_id_list_for_highcharts=Markup(execution_id_list_for_highcharts),
                                   passed_count_list=passed_count_list,
                                   failed_count_list=failed_count_list,
                                   projectname=projectname,
                                   rows_count_for_project=rows_count_for_project,
                                   per_page=per_page,
                                   page=page,
                                   rows_for_project_in_execution_summary=rows_for_project_in_execution_summary)
        if projectname is None:
            project_names = []

            for row in db.session.query(ExecutionSummary.project_name.distinct().label('project_name')):
                project_names.append(row.project_name)

            import json
            return json.dumps({"project_names": project_names})

    except BaseException:
        traceback.print_exc()
        framework_logger.error(traceback.format_exc())
        return render_template("404.html")


@app.route('/execution_id/<string:execution_id>')
@app.route('/execution_id/<string:execution_id>/<int:page>/')
def execution_id_summary(execution_id=None, page=None):
    try:
        if page is None:
            page = 1

        per_page_for_failed_tc = 6
        # per_page_for_passed_tc = 200

        rerun_flag = ExecutionSummary.query.filter_by(execution_id=execution_id).first().rerun_flag
        # if execution_id is not None, then show the execution logs
        fail_testcases_for_count = ExecutionLogs.query.filter_by(execution_id=execution_id, status='fail').order_by(
            "testcase_full_path").all()

        if len(fail_testcases_for_count) == 0:
            fail_testcases_for_count = None

        if fail_testcases_for_count:
            fail_testcases_count = len(fail_testcases_for_count)
        else:
            fail_testcases_count = 0

        if rerun_flag:
            fail_testcases_count = int(fail_testcases_count / 2)

        fail_testcases = ExecutionLogs.query.filter_by(execution_id=execution_id, status='fail').order_by(
            "testcase_full_path").paginate(page=page, per_page=per_page_for_failed_tc)

        pass_testcases = ExecutionLogs.query.filter_by(execution_id=execution_id, status='pass').order_by(
            "testcase_full_path").all()

        if len(pass_testcases) == 0:
            pass_testcases = None

        if pass_testcases:
            pass_testcases_count = len(pass_testcases)
        else:
            pass_testcases_count = 0

        project_name = ExecutionSummary.query.filter_by(execution_id=execution_id).first().project_name

        execution_summary_obj = ExecutionSummary.query.filter_by(execution_id=execution_id).first()

        str_high_chart_for_exec_id = """
                    $(function () {
                        $('.chart_div').highcharts({
                            chart: {
                                type: 'pie',
                                options3d: {
                                    enabled: true,
                                    alpha: 50,
                                    beta: 0
                                }
                            },
                            credits: {
                                enabled: false
                            },
                            colors:[
                                '#3978cc',
                                '#DC3912'
                              ],
                            title: {
                                text: ''
                            },
                            tooltip: {
                                pointFormat: '{series.name}: <b>{point.percentage:.1f}%%</b>'
                            },
                            plotOptions: {
                                pie: {
                                    size:'90%%',
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                    depth: 30,
                                    dataLabels: {
                                        enabled: true,
                                        formatter: function(){
                                            return this.point.name+"-"+this.percentage.toFixed(1)+"%%";
                                        }
                                    }
                                }
                            },
                            series: [{
                                type: 'pie',
                                name: 'Testcase Result',
                                data: [
                                    ['Passed',   %s],
                                    ['Failed',   %s]
                                ]
                            }]
                        });
                    });
             
            """ % (
            pass_testcases_count,
            fail_testcases_count)

        # pass_testcases = ExecutionLogs.query.filter_by(status='pass').filter_by(execution_id=execution_id).order_by(
        #     "testcase_full_path").paginate(page=page, per_page=per_page_for_passed_tc)

        return render_template("testcaes_execution_id.html",
                               str_high_chart_for_exec_id=Markup(str_high_chart_for_exec_id),
                               execution_id=execution_id,
                               fail_testcases=fail_testcases,
                               pass_testcases=pass_testcases,
                               project_name=project_name,
                               page=page,
                               per_page_for_failed_tc=per_page_for_failed_tc,
                               # per_page_for_passed_tc=per_page_for_passed_tc,
                               fail_testcases_count=fail_testcases_count,
                               pass_testcases_count=pass_testcases_count,
                               execution_summary_obj=execution_summary_obj,
                               rerun_flag=rerun_flag)
    except BaseException:
        traceback.print_exc()
        framework_logger.error(traceback.format_exc())
        return render_template("404.html")


@app.route("/")
@app.route('/index')
def home():
    project_list_for_highcharts = ''
    passed_count_list = ''
    failed_count_list = ''

    # get all the executed project/jenkonsjob name list
    project_names = []
    for row in db.session.query(ExecutionSummary.project_name.distinct().label('project_name')):
        project_names.append(row.project_name)

    for pn in sorted(project_names, reverse=False):
        project_list_for_highcharts += u"'" + pn + u"',"

    project_latest_execid_dict = {}

    # get all the project's latest execution_id, on home page will show all the project's latest execution summary
    for pname in project_names:
        row = ExecutionSummary.query.filter_by(project_name=pname).order_by(desc("execution_id")).first()
        project_latest_execid_dict[pname] = row

    row_count = len(project_latest_execid_dict.keys())
    project_latest_execid_dict = collections.OrderedDict(
        sorted(project_latest_execid_dict.items(), reverse=False))

    for key in project_latest_execid_dict.keys():
        passed_count_list += str(project_latest_execid_dict[key].pass_testcases_count) + ','
        failed_count_list += str(project_latest_execid_dict[key].fail_testcases_count) + ','

    return render_template("home.html",
                           projectnames=project_names,
                           project_latest_execid_dict=project_latest_execid_dict,
                           row_count=row_count,
                           project_list_for_highcharts=Markup(project_list_for_highcharts),
                           passed_count_list=passed_count_list,
                           failed_count_list=failed_count_list)


@app.route("/detail/<int:id>")
def detail(id=None):
    try:
        testcase_log_info = ExecutionLogs.query.get(id)

        client = ExecutionSummary.query.filter_by(execution_id=testcase_log_info.execution_id).first().client
        if testcase_log_info is None:
            framework_logger.error("there are no data found for id:", id)
            raise BaseException("there are no data found for id: ", id)

        screenshot_list = []
        if testcase_log_info.screenshots:
            for screenshot in testcase_log_info.screenshots.split(";"):
                if screenshot:
                    screenshot_list.append("/static/screenshots/" + screenshot)
                    # todo: after testcase execution done, copy the output to /static/screenshots/
    except BaseException:
        traceback.print_exc()
        framework_logger.error(traceback.format_exc())
        return render_template('404.html')

    return render_template("testcase_details.html",
                           testcase=testcase_log_info,
                           project_name=testcase_log_info.project_name,
                           execution_id=testcase_log_info.execution_id,
                           id=testcase_log_info.id,
                           client=client,
                           screenshot_list=screenshot_list
                           )


@app.route("/history/<int:id>")
def history(id=None):
    testcase_log_info = ExecutionLogs.query.get(id)
    project_name = testcase_log_info.project_name
    testcase_full_path = testcase_log_info.testcase_full_path

    execution_id_list = []
    rows = ExecutionSummary.query.filter_by(project_name=project_name).order_by(
        desc(ExecutionSummary.execution_id)).limit(30).all()
    # rows = ExecutionSummary.query.filter_by(project_name=project_name).limit(30).all()
    if len(rows) == 0:
        execution_id_list = None
    else:
        for row in rows:
            execution_id_list.append(row.execution_id)
        execution_id_list.sort(reverse=True)

    map_for_testcase_id_in_db_and_execution_id = {}
    # 有可能某些execution_id对应的logs中没有找到指定的 testcase（即：相应的execution_id 此次并没有运行指定的testcase, 此处过滤一下
    execution_id_list_for_history = []
    execution_id_list_for_history_fail_count = 0
    execution_id_list_for_history_pass_count = 0

    for exec_id in execution_id_list:
        row = ExecutionLogs.query.filter_by(execution_id=exec_id).filter_by(
            testcase_full_path=testcase_full_path).first()

        if row is not None:
            execution_id_list_for_history.append(exec_id)
            row_in_summary = ExecutionSummary.query.filter_by(execution_id=exec_id).first()
            row.env = row_in_summary.environment
            row.client = row_in_summary.client
            map_for_testcase_id_in_db_and_execution_id[exec_id] = row

            if ExecutionLogs.query.filter_by(testcase_full_path=testcase_full_path,
                                             execution_id=exec_id).first().status == "fail":
                execution_id_list_for_history_fail_count += 1

            if ExecutionLogs.query.filter_by(testcase_full_path=testcase_full_path,
                                             execution_id=exec_id).first().status == "pass":
                execution_id_list_for_history_pass_count += 1

    execution_id_list_for_history_count = len(execution_id_list_for_history)

    return render_template("testcase_history.html",
                           project_name=project_name,
                           tc_id_exec_id_map=map_for_testcase_id_in_db_and_execution_id,
                           testcase_full_path=testcase_full_path,
                           execution_id_list_for_history=execution_id_list_for_history,
                           execution_id_list_for_history_count=execution_id_list_for_history_count,
                           execution_id_list_for_history_fail_count=execution_id_list_for_history_fail_count,
                           execution_id_list_for_history_pass_count=execution_id_list_for_history_pass_count, )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(user_name=data["name"]).first()
        # user = User.query.filter((User.user_name==data["name"])|(User.email==data["name"])).first()

        if user is None:
            flash("Account not exists!", "err")
            return redirect(url_for("login"))

        if not user.check_pwd(data["pwd"]):
            flash("Password Error！", "err")
            return redirect(url_for("login"))
        session["user"] = user.user_name
        session["user_id"] = user.id

        return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    # redirect to home page after click logout
    return redirect(url_for("home"))


@app.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        user = User(
            user_name=form.user_name.data,
            password=form.pwd.data,
            email=form.email.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("Register Success", "ok")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/user/")
def user():
    return render_template('user.html')


@app.route("/pwd/")
def pwd():
    return render_template('pwd.html')


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    # app.debug = True
    app.run(debug=True)
