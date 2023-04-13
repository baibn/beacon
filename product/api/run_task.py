from product.case.models import CaseGroup, CaseManage, CaseTask
from product.result.models import Result
from product.utils.tools import login_required, get_user, model_to_dict, send_mail
from product.utils.HTMLTestRunner import HTMLTestRunner
from product import db, app
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint
import unittest
from product.utils.Test import Test, __generate_testcases
from product.config import Config
from datetime import datetime
import os

run_task = Blueprint('runtask', __name__)


@run_task.route('', methods=('POST',))
@login_required
def case_run_task():
    token = request.headers["token"]
    task_id = request.get_json().get('taskId')
    if CaseTask.query.filter_by(task_id=task_id).first().status == 1:
        task_namme = CaseTask.query.filter_by(task_id=task_id).first().task_name
        group_id_list = [int(i) for i in CaseTask.query.filter_by(task_id=task_id).first().task_group.split(',')]
        db_cases = []
        for group_id in group_id_list:
            if CaseGroup.query.filter_by(group_id=group_id).first().status != 0:
                db_cases_by_group = CaseManage.query.filter(CaseManage.group_id == group_id,
                                                            CaseManage.status == 1).all()
                db_cases += db_cases_by_group
            else:
                return jsonify({"code": 300, "message": "任务中有禁用状态的用例集！"})
        case_list = []
        for case in db_cases:
            case_dict = model_to_dict(case)
            case_list.append(case_dict)
        __generate_testcases(case_list)
        suit = unittest.makeSuite(Test)
        reportname = 'API_AutoTest_{0}_report{1}.html'.format(task_namme,
                                                              datetime.now().strftime("%Y%m%d_%H%M%S"))
        report = os.path.join(Config.REPORT_PATH, reportname)
        report_link = "http://auto-qa.ishumei.com/static/" + reportname
        title = '接口自动化测试报告%s' % datetime.now().strftime("%Y%m%d%H%M%S")
        fp = open(report, 'wb')
        runner = HTMLTestRunner(stream=fp, verbosity=2, title=title,
                                description=report_link)
        runner.run(suit)
        operate_by = get_user(token)
        case_run_way = 1
        record = Result(task_id=task_id, case_run_way=case_run_way, operate_by=operate_by, result=report_link)
        try:
            db.session.add(record)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 300, "message": str(e)})
        subject = "接口自动化测试报告"
        body = "Hi,附件是本次接口自动化测试报告。报告链接:{0}\nBy beacon".format(report_link)
        send_to = CaseTask.query.filter_by(task_id=task_id).first().email
        if send_to is not None:
            send_list = []
            send_list.append(send_to)
            try:
                send_mail(subject=subject, sender=app.config['MAIL_USERNAME'], recipients=send_list, body=body, file=report)
            except Exception as e:
                return jsonify({"code": 300, "message": str(e)})
        return jsonify({"code": 200, "message": "success!稍后查看报告"})
    else:
        return jsonify({"code": 300, "message": "禁用状态的任务不能执行！"})
