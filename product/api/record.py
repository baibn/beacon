from product.utils.tools import login_required
from product.result.models import Result
from flask import request, jsonify
from flask import Blueprint
from product.case.models import CaseTask, CaseGroup

record = Blueprint('record', __name__)


@record.route('/list', methods=('POST',))
@login_required
def record_list():
    records_data = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    if 'taskId' in request.get_json().keys():
        task_id = request.get_json().get('taskId')
        db_records = Result.query.filter_by(task_id=task_id).order_by(
                Result.operate_at.desc()).all()
        if len(db_records) != 0:
            for data in db_records:
                if data.case_run_way == 1:
                    case_run_way_cn = "手动"
                else:
                    case_run_way_cn = "自动"
                task_name = CaseTask.query.filter_by(task_id=task_id).first().task_name
                record_data = {"RecordId": data.record_id, "taskName": task_name, "groupName": "",
                               "caseRunWay": case_run_way_cn,
                               "operateAt": data.operate_at.strftime("%Y-%m-%d %H:%M:%S"),
                               "operateBy": data.operate_by, "result": data.result}
                records_data.append(record_data)
            start = (page - 1) * limit
            end = page * limit if len(records_data) > page * limit else start + len(records_data)
            ret = records_data[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(records_data), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    elif 'groupId' in request.get_json().keys():
        group_id = request.get_json().get('groupId')
        db_records = Result.query.filter_by(group_id=group_id).order_by(
                Result.operate_at.desc()).all()
        if len(db_records) != 0:
            for data in db_records:
                if data.case_run_way == 1:
                    case_run_way_cn = "手动"
                else:
                    case_run_way_cn = "自动"
                group_name = CaseGroup.query.filter_by(group_id=group_id).first().group_name
                record_data = {"RecordId": data.record_id, "taskId": "", "groupId": group_name,
                               "caseRunWay": case_run_way_cn,
                               "operateAt": data.operate_at.strftime("%Y-%m-%d %H:%M:%S"),
                               "operateBy": data.operate_by, "result": data.result}
                records_data.append(record_data)
            start = (page - 1) * limit
            end = page * limit if len(records_data) > page * limit else start + len(records_data)
            ret = records_data[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(records_data), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        return jsonify(
            {"code": 300, "message": "缺少查询参数!"})
