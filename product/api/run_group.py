from product.case.models import CaseGroup, CaseManage
from product.result.models import Result
from product.utils.tools import login_required, get_user, model_to_dict
from product.utils.HTMLTestRunner import HTMLTestRunner
from product import db
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint
import unittest
from product.utils.Test import Test, __generate_testcases
from product.config import Config
from datetime import datetime
import os

run_group = Blueprint('rungroup', __name__)


@run_group.route('', methods=('POST',))
@login_required
def case_run_group():
    token = request.headers["token"]
    group_id = request.get_json().get('groupId')
    if CaseGroup.query.filter_by(group_id=group_id).first().status == 1:
        group_namme = CaseGroup.query.filter_by(group_id=group_id).first().group_name
        db_cases = CaseManage.query.filter(CaseManage.group_id == group_id, CaseManage.status == 1).all()
        case_list = []
        for case in db_cases:
            case_dict = model_to_dict(case)
            case_list.append(case_dict)
        __generate_testcases(case_list)
        suit = unittest.makeSuite(Test)
        reportname = 'API_AutoTest_{0}_report{1}.html'.format(group_namme,
                                                              datetime.now().strftime("%Y%m%d_%H%M%S"))
        report = os.path.join(Config.REPORT_PATH, reportname)
        title = '接口自动化测试报告%s' % datetime.now().strftime("%Y%m%d%H%M%S")
        fp = open(report, 'wb')
        report_link = "http://auto-qa.ishumei.com/static/" + reportname
        runner = HTMLTestRunner(stream=fp, verbosity=2, title=title,
                                description=report_link)
        runner.run(suit)
        operate_by = get_user(token)
        case_run_way = 1
        report_link = "http://auto-qa.ishumei.com/static/" + reportname
        record = Result(group_id=group_id, case_run_way=case_run_way, operate_by=operate_by, result=report_link)
        try:
            db.session.add(record)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 300, "message": str(e)})
        return jsonify({"code": 200, "message": "success!稍后查看报告"})

    else:
        return jsonify({"code": 300, "message": "禁用状态下的用例集不能执行！"})
