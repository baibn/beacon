// Copyright (c) 2015 SHUMEI Inc. All rights reserved.
// Authors: Liang Kun <liangkun@ishumei.com>.

//namespace cpp2 com.shumei.service
//namespace cpp com.shumei.service
//namespace php com.shumei.service
//namespace java com.shumei.service

namespace py fgen

// 所属领域类型
const string TYPE_ECOM = "ECOM"      // 电商
const string TYPE_ZHIBO = "ZHIBO"    // 直播

// 预测请求
struct PredictRequest {
    1: optional string requestId;       // 唯一标识本次请求
    2: optional string serviceId;       // 唯一标识一个服务
    3: optional string type;            // 请求所属领域类型
    4: optional string organization;    // 唯一标识一个组织
    5: optional string appId;           // 唯一标识一个业务
    9: optional string eventId;         // 标识一个事件
    6: optional string tokenId;         // 唯一标识一个用户
    7: optional i64 timestamp;          // 客户端时间戳
    8: optional string data;            // 请求数据内容，JSON字符串
    10: optional set<string> operation; // data operation
    11: optional set<string> tags;      // flow tags
}

// 风险级别
const string RISK_LEVEL_PASS = "PASS"      // 放行
const string RISK_LEVEL_REVIEW = "REVIEW"  // 需要再次确认
const string RISK_LEVEL_REJECT = "REJECT"  // 拒绝

// 预测结果
struct PredictResult {
    1: optional i32 score;         // [0, 1000], 风险越大，分数越高
    2: optional string riskLevel;  // 风险级别
    3: optional string detail;     // 风险详情，JSON字符串
}

// 异常代码
const string CODE_INVALID_ARGUMENT = "InvalidArgument"  // 参数错误
const string CODE_BE_ERROR = "BasicEngineError"         // 基础引擎错误

// 预测器异常
exception PredictException {
    1: optional string code;     // 异常代码
    2: optional string message;  // 异常消息
}

// 预测器（服务）
service Predictor {
    // 完成预测
    PredictResult predict(1:PredictRequest request) throws (1: PredictException e);

    // 返回当前预测器版本
    string version();
}
