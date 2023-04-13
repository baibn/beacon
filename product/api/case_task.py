from product.case.models import CaseTask, CaseGroup
from product.utils.tools import login_required, get_user
from product import db, scheduler, app
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint
from apscheduler.triggers.cron import CronTrigger
from product.utils.Test import run_case_0

case_task = Blueprint('casetask', __name__)


@case_task.route('/create', methods=('POST',))
@login_required
def case_task_create():
    token = request.headers["token"]
    task_name = request.get_json().get('taskName')
    task_group = request.get_json().get('taskGroup')
    group_id_string = ",".join('%s' % id for id in task_group)
    case_run_way = request.get_json().get('caseRunWay')
    if case_run_way == 0:
        case_run_way_0 = request.get_json().get('caseRunWay0')
    else:
        case_run_way_0 = "0 24 * * *"
    create_by = get_user(token)
    status = request.get_json().get('status')
    db_task_by_name = CaseTask.query.filter_by(task_name=task_name).first()
    if db_task_by_name:
        return jsonify({"code": 300, "message": "任务名称已被占用，请更换后重新提交！"})
    if int(case_run_way) not in [0, 1]:
        return jsonify({"code": 300, "message": "执行方式不合法！"})
    if 'email' in request.get_json().keys():
        email = request.get_json().get('email')
        task = CaseTask(task_name=task_name, task_group=group_id_string, case_run_way=case_run_way,
                        case_run_way_0=case_run_way_0, create_by=create_by, email=email,
                        update_by=create_by, status=status)
    else:
        task = CaseTask(task_name=task_name, task_group=group_id_string, case_run_way=case_run_way,
                        case_run_way_0=case_run_way_0, create_by=create_by,
                        update_by=create_by, status=status)
    try:
        db.session.add(task)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    insert_task_data = CaseTask.query.filter_by(task_name=task_name).first()
    group_id_list = [int(i) for i in insert_task_data.task_group.split(',')]
    data = {"taskId": insert_task_data.task_id, "taskName": insert_task_data.task_name,
            "taskGroup": group_id_list,
            "caseRunWay": insert_task_data.case_run_way, "caseRunWay0": insert_task_data.case_run_way_0,
            "createBy": insert_task_data.create_by, "updateBy": insert_task_data.update_by,
            "createAt": insert_task_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updateAt": insert_task_data.update_at.strftime("%Y-%m-%d %H:%M:%S"), "isDel": insert_task_data.is_del,
            "status": insert_task_data.status, "email": insert_task_data.email}
    # 判断任务执行方式和状态，添加定时任务
    if insert_task_data.status == 1 and insert_task_data.case_run_way == 0:
        # APScheduler触发器triggers为cron的时候，支持cron表达式，但是只支持五位，即minute, hour, day, month,day_of_week
        operate_by = get_user(token)
        send_by = app.config['MAIL_USERNAME']
        task_id = CaseTask.query.filter_by(task_name=task_name).first().task_id
        try:
            scheduler.add_job(func=run_case_0, args=(insert_task_data, operate_by, send_by,), id=str(task_id),
                              trigger=CronTrigger.from_crontab(case_run_way_0))
        except Exception as e:
            return jsonify({"code": 300, "message": str(e)})
    return jsonify({"code": 200, "message": "添加成功", "content": data})


@case_task.route('/update', methods=('POST',))
@login_required
def case_task_update():
    token = request.headers["token"]
    task_id = request.get_json().get('taskId')
    task_name = request.get_json().get('taskName')
    task_group = request.get_json().get('taskGroup')
    group_id_string = ",".join('%s' % id for id in task_group)
    case_run_way = request.get_json().get('caseRunWay')
    if case_run_way == 0:
        case_run_way_0 = request.get_json().get('caseRunWay0')
    else:
        case_run_way_0 = "0 24 * * *"
    update_by = get_user(token)
    status = request.get_json().get('status')
    db_task = CaseTask.query.filter_by(task_name=task_name).first()
    if db_task and db_task.task_id != task_id:
        return jsonify({"code": 300, "message": "任务名称已被占用，请更换后重新提交！"})
    if int(case_run_way) not in [0, 1]:
        return jsonify({"code": 300, "message": "执行方式必须是0或1!"})

    task = CaseTask.query.get(task_id)
    if task:
        if 'email' in request.get_json().keys():
            email = request.get_json().get('email')
            task.task_name = task_name
            task.task_group = group_id_string
            task.case_run_way = case_run_way
            task.case_run_way_0 = case_run_way_0
            task.update_by = update_by
            task.status = status
            task.email = email
        else:
            task.task_name = task_name
            task.task_group = group_id_string
            task.case_run_way = case_run_way
            task.case_run_way_0 = case_run_way_0
            task.update_by = update_by
            task.status = status
        try:
            db.session.add(task)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 300, "message": str(e)})
        update_task_data = CaseTask.query.filter_by(task_id=task_id).first()
        group_id_list = [int(s) for s in update_task_data.task_group.split(',')]
        group_name_list = []
        for i in group_id_list:
            name = CaseGroup.query.filter_by(group_id=i).first().group_name
            group_name_list.append(name)
        data = {"taskId": update_task_data.task_id, "task_name": update_task_data.task_name,
                "taskGroup": group_name_list,
                "caseRunWay": update_task_data.case_run_way, "caseRunWay0": update_task_data.case_run_way_0,
                "createBy": update_task_data.create_by, "updateBy": update_task_data.update_by,
                "createAt": update_task_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": update_task_data.update_at.strftime("%Y-%m-%d %H:%M:%S"), "isDel": update_task_data.is_del,
                "status": update_task_data.status, "email": update_task_data.email}
        # 判断任务执行方式和状态，添加定时任务
        if update_task_data.status == 1 and update_task_data.case_run_way == 0:
            if str(task_id) not in scheduler.get_jobs():
                operate_by = get_user(token)
                send_by = app.config['MAIL_USERNAME']
                task_id = CaseTask.query.filter_by(task_name=task_name).first().task_id
                try:
                    scheduler.add_job(func=run_case_0, args=(update_task_data, operate_by, send_by,), id=str(task_id),
                                      trigger=CronTrigger.from_crontab(case_run_way_0))
                except Exception as e:
                    return jsonify({"code": 300, "message": str(e)})
            else:
                try:
                    scheduler.resume_job(str(task_id))
                except Exception as e:
                    return jsonify({"code": 300, "message": str(e)})
        elif update_task_data.status == 0 and update_task_data.case_run_way == 0:
            if str(task_id) in scheduler.get_jobs():
                try:
                    scheduler.pause_job(str(task_id))
                except Exception as e:
                    return jsonify({"code": 300, "message": str(e)})
        return jsonify({"code": 200, "message": "修改成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "用例计划不存在"})


@case_task.route('/detail', methods=('POST',))
@login_required
def case_task_detail():
    task_id = request.get_json().get('taskId')
    db_task = CaseTask.query.filter_by(task_id=task_id).first()
    if db_task:
        data = {"taskId": db_task.task_id, "task_name": db_task.task_name,
                "taskGroup": db_task.task_group,
                "caseRunWay": db_task.case_run_way, "caseRunWay0": db_task.case_run_way_0,
                "createBy": db_task.create_by, "updateBy": db_task.update_by,
                "createAt": db_task.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": db_task.update_at.strftime("%Y-%m-%d %H:%M:%S"), "isDel": db_task.is_del,
                "status": db_task.status, "email": db_task.email}
        return jsonify({"code": 300, "message": "修改成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "用例计划不存在"})


@case_task.route('/list', methods=('POST',))
@login_required
def case_task_list():
    tasks_data = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    if 'taskName' not in request.get_json().keys():
        db_tasks = CaseTask.query.filter_by(is_del=0).order_by(
                            CaseTask.update_at.desc()).all()
        if len(db_tasks) != 0:
            for task in db_tasks:
                group_id_list = [int(s) for s in task.task_group.split(',')]
                group_name_list = []
                for i in group_id_list:
                    name = CaseGroup.query.filter_by(group_id=i).first().group_name
                    group_name_list.append(name)
                group_name_string = ",".join(group_name_list)
                if task.case_run_way == 0:
                    case_run_way_cn = "自动任务"
                else:
                    case_run_way_cn = "手动任务"
                task_data = {"taskId": task.task_id, "taskName": task.task_name, "taskGroup": group_id_list,
                             "taskGroupString": group_name_string, "caseRunWay": task.case_run_way,
                             "caseRunWayCN": case_run_way_cn, "caseRunWay0": task.case_run_way_0,
                             "createBy": task.create_by, "updateBy": task.update_by,
                             "email": task.email, "createAt": task.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                             "updateAt": task.update_at.strftime("%Y-%m-%d %H:%M:%S"), "isDel": task.is_del,
                             "status": task.status}
                tasks_data.append(task_data)
            start = (page - 1) * limit
            end = page * limit if len(tasks_data) > page * limit else start + len(tasks_data)
            ret = tasks_data[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(tasks_data), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        task_name = request.get_json().get('taskName')
        db_tasks = CaseTask.query.filter(CaseTask.is_del == 0,
                                         CaseTask.task_name.like('%{keyword}%'.format(keyword=task_name))).order_by(
                            CaseTask.update_at.desc()).all()
        if len(db_tasks) != 0:
            for task in db_tasks:
                group_id_list = [int(s) for s in task.task_group.split(',')]
                group_name_list = []
                for i in group_id_list:
                    name = CaseGroup.query.filter_by(group_id=i).first().group_name
                    group_name_list.append(name)
                group_name_string = ",".join(group_name_list)
                if task.case_run_way == 0:
                    case_run_way_cn = "自动任务"
                else:
                    case_run_way_cn = "手动任务"
                task_data = {"taskId": task.task_id, "taskName": task.task_name, "taskGroup": group_id_list,
                             "taskGroupString": group_name_string, "caseRunWay": task.case_run_way,
                             "caseRunWayCN": case_run_way_cn, "caseRunWay0": task.case_run_way_0,
                             "createBy": task.create_by, "updateBy": task.update_by,
                             "email": task.email, "createAt": task.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                             "updateAt": task.update_at.strftime("%Y-%m-%d %H:%M:%S"), "isDel": task.is_del,
                             "status": task.status}
                tasks_data.append(task_data)
            start = (page - 1) * limit
            end = page * limit if len(tasks_data) > page * limit else start + len(tasks_data)
            ret = tasks_data[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(tasks_data), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@case_task.route('/delete', methods=('POST',))
@login_required
def case_task_delete():
    request_data = request.get_json()
    task_id = request_data.get('taskId')
    task = CaseTask.query.get(task_id)
    if not task:
        return jsonify({"code": 300, "message": "用例计划不存在"})
    if task.status == 1:
        return jsonify({"code": 300, "message": "启用状态下的用例计划不可删除"})
    task.is_del = 1  # 逻辑删除
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    if task_id in scheduler.get_jobs():
        try:
            scheduler.remove_job(str(task_id))
        except Exception as e:
            return jsonify({"code": 300, "message": str(e)})
    return jsonify({"code": 200, "message": "删除成功！"})
