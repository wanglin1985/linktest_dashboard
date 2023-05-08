from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@127.0.0.1/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a random string'

db = SQLAlchemy(app)


class ExecutionLogs(db.Model):
    """ testcase model """
    __tablename__ = 'execution_logs'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    execution_id = db.Column(db.String(50), nullable=False)
    # execution_id = db.Column(db.String(100), db.ForeignKey('execution_summary.execution_id'))

    tc_id = db.Column(db.String(50))
    tc_name = db.Column(db.String(100), nullable=False)
    file = db.Column(db.String(300), nullable=False)
    testcase_full_path = db.Column(db.String(350), nullable=False)
    execution_time = db.Column(db.String(50))
    status = db.Column(db.String(10), nullable=False)
    error_info = db.Column(db.Text)
    execution_log = db.Column(db.Text)
    tags = db.Column(db.Text)
    package_list = db.Column(db.Text)
    jenkins_job_name = db.Column(db.Text)
    rerun_flag = db.Column(db.Boolean, default=False)
    # rerun_flag = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    screenshots = db.Column(db.Text)
    testcase_start_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<TestCaseLogs %r>' % self.execution_id


class ExecutionSummary(db.Model):
    __tablename__ = 'execution_summary'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    execution_id = db.Column(db.String(50), nullable=False)
    environment = db.Column(db.String(100))
    os = db.Column(db.String(100))
    automation_framework_version = db.Column(db.String(100))
    total_execution_time = db.Column(db.String(100))
    jenkins_job_name = db.Column(db.Text)
    project_name = db.Column(db.String(100), nullable=False)
    total_testcases_count = db.Column(db.Integer)
    pass_testcases_count = db.Column(db.Integer)
    fail_testcases_count = db.Column(db.Integer)
    client = db.Column(db.String(255))
    rerun_flag = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<ExecutionSummary %r>' % self.execution_id


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.user_name

    def check_pwd(self, pwd):
        # from werkzeug.security import check_password_hash
        # return check_password_hash(self.password, pwd)
        return self.password == pwd
