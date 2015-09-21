#lambdaimage文档
##环境需求

- python2.7
- spark1.3.0
- hadoop1.0

##环境配置:
###spark环境配置
主节点: blade12
计算节点: blade13 blade16 blade17

###hadoop环境配置
主节点: blade12
数据节点: blade13 blade16 blade17

###lambdaimage环境配置

- PYTHONPATH: 



##项目结构
###主目录

- lambdaimage            主目录
 | + doc                 文档
 | + test                单元测试
 | + script              可执行脚本
 | + lambdaimage         核心代码
 | -Makefile             C代码编译规则
 | -requirements.txt     需求的python库
 | -setup                安装规则

###核心代码目录


